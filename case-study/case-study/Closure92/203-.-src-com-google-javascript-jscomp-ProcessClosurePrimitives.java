

package com.google.javascript.jscomp;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.google.javascript.jscomp.NodeTraversal.AbstractPostOrderCallback;
import com.google.javascript.rhino.Node;
import com.google.javascript.rhino.Token;

import java.util.List;
import java.util.Map;
import java.util.Set;


class ProcessClosurePrimitives extends AbstractPostOrderCallback
    implements CompilerPass {

  static final DiagnosticType NULL_ARGUMENT_ERROR = DiagnosticType.error(
      "JSC_NULL_ARGUMENT_ERROR",
      "method \"{0}\" called without an argument");

  static final DiagnosticType INVALID_ARGUMENT_ERROR = DiagnosticType.error(
      "JSC_INVALID_ARGUMENT_ERROR",
      "method \"{0}\" called with a non-string argument");

  static final DiagnosticType TOO_MANY_ARGUMENTS_ERROR = DiagnosticType.error(
      "JSC_TOO_MANY_ARGUMENTS_ERROR",
      "method \"{0}\" called with more than one argument");

  static final DiagnosticType DUPLICATE_NAMESPACE_ERROR = DiagnosticType.error(
      "JSC_DUPLICATE_NAMESPACE_ERROR",
      "namespace \"{0}\" cannot be provided twice");

  static final DiagnosticType FUNCTION_NAMESPACE_ERROR = DiagnosticType.error(
      "JSC_FUNCTION_NAMESPACE_ERROR",
      "\"{0}\" cannot be both provided and declared as a function");

  static final DiagnosticType MISSING_PROVIDE_ERROR = DiagnosticType.error(
      "JSC_MISSING_PROVIDE_ERROR",
      "required \"{0}\" namespace never provided");

  static final DiagnosticType LATE_PROVIDE_ERROR = DiagnosticType.error(
      "JSC_LATE_PROVIDE_ERROR",
      "required \"{0}\" namespace not provided yet");

  static final DiagnosticType INVALID_PROVIDE_ERROR = DiagnosticType.error(
      "JSC_INVALID_PROVIDE_ERROR",
      "\"{0}\" is not a valid JS property name");

  static final DiagnosticType XMODULE_REQUIRE_ERROR = DiagnosticType.warning(
      "JSC_XMODULE_REQUIRE_ERROR",
      "namespace \"{0}\" provided in module {1} " +
      "but required in module {2}");

  static final DiagnosticType NON_STRING_PASSED_TO_SET_CSS_NAME_MAPPING_ERROR =
      DiagnosticType.error(
          "JSC_NON_STRING_PASSED_TO_SET_CSS_NAME_MAPPING_ERROR",
      "goog.setCssNameMapping only takes an object literal with string values");

  static final DiagnosticType BASE_CLASS_ERROR = DiagnosticType.error(
      "JSC_BASE_CLASS_ERROR",
      "incorrect use of goog.base: {0}");

  
  static final String GOOG = "goog";

  private final AbstractCompiler compiler;
  private final JSModuleGraph moduleGraph;

  
  private final Map<String, ProvidedName> providedNames =
      Maps.newTreeMap();

  private final List<UnrecognizedRequire> unrecognizedRequires =
      Lists.newArrayList();
  private final Set<String> exportedVariables = Sets.newHashSet();
  private final CheckLevel requiresLevel;
  private final boolean rewriteNewDateGoogNow;

  ProcessClosurePrimitives(AbstractCompiler compiler,
                           CheckLevel requiresLevel,
                           boolean rewriteNewDateGoogNow) {
    this.compiler = compiler;
    this.moduleGraph = compiler.getModuleGraph();
    this.requiresLevel = requiresLevel;
    this.rewriteNewDateGoogNow = rewriteNewDateGoogNow;

    
    providedNames.put(GOOG,
        new ProvidedName(GOOG, null, null, false ));
  }

  Set<String> getExportedVariableNames() {
    return exportedVariables;
  }

  @Override
  public void process(Node externs, Node root) {
    new NodeTraversal(compiler, this).traverse(root);

    for (ProvidedName pn : providedNames.values()) {
      pn.replace();
    }

    if (requiresLevel.isOn()) {
      for (UnrecognizedRequire r : unrecognizedRequires) {
        DiagnosticType error;
        ProvidedName expectedName = providedNames.get(r.namespace);
        if (expectedName != null && expectedName.firstNode != null) {
          
          error = LATE_PROVIDE_ERROR;
        } else {
          error = MISSING_PROVIDE_ERROR;
        }

        compiler.report(JSError.make(
            r.inputName, r.requireNode, requiresLevel, error, r.namespace));
      }
    }
  }

  @Override
  public void visit(NodeTraversal t, Node n, Node parent) {
    switch (n.getType()) {
      case Token.CALL:
        boolean isExpr = parent.getType() == Token.EXPR_RESULT;
        Node left = n.getFirstChild();
        if (left.getType() == Token.GETPROP) {
          Node name = left.getFirstChild();
          if (name.getType() == Token.NAME &&
              GOOG.equals(name.getString())) {
            
            
            
            String methodName = name.getNext().getString();
            if ("base".equals(methodName)) {
              processBaseClassCall(t, n);
            } else if (!isExpr) {
              
              break;
            } else if ("require".equals(methodName)) {
              processRequireCall(t, n, parent);
            } else if ("provide".equals(methodName)) {
              processProvideCall(t, n, parent);
            } else if ("exportSymbol".equals(methodName)) {
              Node arg = left.getNext();
              if (arg.getType() == Token.STRING) {
                int dot = arg.getString().indexOf('.');
                if (dot == -1) {
                  exportedVariables.add(arg.getString());
                } else {
                  exportedVariables.add(arg.getString().substring(0, dot));
                }
              }
            } else if ("addDependency".equals(methodName)) {
              CodingConvention convention = compiler.getCodingConvention();
              List<String> typeDecls =
                  convention.identifyTypeDeclarationCall(n);
              if (typeDecls != null) {
                for (String typeDecl : typeDecls) {
                  compiler.getTypeRegistry().forwardDeclareType(typeDecl);
                }
              }

              
              
              parent.replaceChild(n, Node.newNumber(0));
              compiler.reportCodeChange();
            } else if ("setCssNameMapping".equals(methodName)) {
              processSetCssNameMapping(t, n, parent);
            }
          }
        }
        break;
      case Token.ASSIGN:
      case Token.NAME:
        
        
        handleCandidateProvideDefinition(t, n, parent);
        break;
      case Token.FUNCTION:
        
        
        if (t.inGlobalScope() &&
            !NodeUtil.isFunctionExpression(n)) {
          String name = n.getFirstChild().getString();
          ProvidedName pn = providedNames.get(name);
          if (pn != null) {
            compiler.report(t.makeError(n, FUNCTION_NAMESPACE_ERROR, name));
          }
        }
        break;

      case Token.NEW:
        trySimplifyNewDate(t, n, parent);
        break;

      case Token.GETPROP:
        if (n.getFirstChild().getType() == Token.NAME &&
            parent.getType() != Token.CALL &&
            parent.getType() != Token.ASSIGN &&
            "goog.base".equals(n.getQualifiedName())) {
          reportBadBaseClassUse(t, n, "May only be called directly.");
        }
        break;
    }
  }

  
  private void processRequireCall(NodeTraversal t, Node n, Node parent) {
    Node left = n.getFirstChild();
    Node arg = left.getNext();
    if (verifyArgument(t, left, arg)) {
      String ns = arg.getString();
      ProvidedName provided = providedNames.get(ns);
      if (provided == null || !provided.isExplicitlyProvided()) {
        unrecognizedRequires.add(
            new UnrecognizedRequire(n, ns, t.getSourceName()));
      } else {
        JSModule providedModule = provided.explicitModule;

        
        Preconditions.checkNotNull(providedModule);

        JSModule module = t.getModule();
        if (moduleGraph != null &&
            module != providedModule &&
            !moduleGraph.dependsOn(module, providedModule)) {
          compiler.report(
              t.makeError(n, XMODULE_REQUIRE_ERROR, ns,
                  providedModule.getName(),
                  module.getName()));
        }
      }

      
      
      
      
      
      
      if (provided != null || requiresLevel.isOn()) {
        parent.detachFromParent();
        compiler.reportCodeChange();
      }
    }
  }

  
  private void processProvideCall(NodeTraversal t, Node n, Node parent) {
    Node left = n.getParent();
    Node arg = left.getNext();
    if (verifyProvide(t, left, arg)) {
      String ns = arg.getString();
      if (providedNames.containsKey(ns)) {
        ProvidedName previouslyProvided = providedNames.get(ns);
        if (!previouslyProvided.isExplicitlyProvided()) {
          previouslyProvided.addProvide(parent, t.getModule(), true);
        } else {
          compiler.report(
              t.makeError(n, DUPLICATE_NAMESPACE_ERROR, ns));
        }
      } else {
        registerAnyProvidedPrefixes(ns, parent, t.getModule());
        providedNames.put(
            ns, new ProvidedName(ns, parent, t.getModule(), true));
      }
    }
  }

  
  private void handleCandidateProvideDefinition(
      NodeTraversal t, Node n, Node parent) {
    if (t.inGlobalScope()) {
      String name = null;
      if (n.getType() == Token.NAME && parent.getType() == Token.VAR) {
        name = n.getString();
      } else if (n.getType() == Token.ASSIGN &&
          parent.getType() == Token.EXPR_RESULT) {
        name = n.getFirstChild().getQualifiedName();
      }

      if (name != null) {
        if (parent.getBooleanProp(Node.IS_NAMESPACE)) {
          processProvideFromPreviousPass(t, name, parent);
        } else {
          ProvidedName pn = providedNames.get(name);
          if (pn != null) {
            pn.addDefinition(parent, t.getModule());
          }
        }
      }
    }
  }

  
  private void processBaseClassCall(NodeTraversal t, Node n) {
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    Node callee = n.getFirstChild();
    Node thisArg = callee.getNext();
    if (thisArg == null || thisArg.getType() != Token.THIS) {
      reportBadBaseClassUse(t, n, "First argument must be 'this'.");
      return;
    }

    Node enclosingFnNameNode = getEnclosingDeclNameNode(t);
    if (enclosingFnNameNode == null) {
      reportBadBaseClassUse(t, n, "Could not find enclosing method.");
      return;
    }

    String enclosingQname = enclosingFnNameNode.getQualifiedName();
    if (enclosingQname.indexOf(".prototype.") == -1) {
      
      Node enclosingParent = enclosingFnNameNode.getParent();
      Node maybeInheritsExpr = (enclosingParent.getType() == Token.ASSIGN ?
          enclosingParent.getParent() : enclosingParent).getNext();
      Node baseClassNode = null;
      if (maybeInheritsExpr != null &&
          maybeInheritsExpr.getType() == Token.EXPR_RESULT &&
          maybeInheritsExpr.getFirstChild().getType() == Token.CALL) {
        Node callNode = maybeInheritsExpr.getFirstChild();
        if ("goog.inherits".equals(
                callNode.getFirstChild().getQualifiedName()) &&
            callNode.getLastChild().isQualifiedName()) {
          baseClassNode = callNode.getLastChild();
        }
      }

      if (baseClassNode == null) {
        reportBadBaseClassUse(
            t, n, "Could not find goog.inherits for base class");
        return;
      }

      
      n.replaceChild(
          callee,
          NodeUtil.newQualifiedNameNode(
            String.format("%s.call", baseClassNode.getQualifiedName()),
            callee, "goog.base"));
      compiler.reportCodeChange();
    } else {
      
      Node methodNameNode = thisArg.getNext();
      if (methodNameNode == null || methodNameNode.getType() != Token.STRING) {
        reportBadBaseClassUse(t, n, "Second argument must name a method.");
        return;
      }

      String methodName = methodNameNode.getString();
      String ending = ".prototype." + methodName;
      if (enclosingQname == null ||
          !enclosingQname.endsWith(ending)) {
        reportBadBaseClassUse(
            t, n, "Enclosing method does not match " + methodName);
        return;
      }

      
      Node className =
          enclosingFnNameNode.getFirstChild().getFirstChild();
      n.replaceChild(
          callee,
          NodeUtil.newQualifiedNameNode(
            String.format("%s.superClass_.%s.call",
                className.getQualifiedName(), methodName),
            callee, "goog.base"));
      n.removeChild(methodNameNode);
      compiler.reportCodeChange();
    }
  }

  
  private Node getEnclosingDeclNameNode(NodeTraversal t) {
    Node scopeRoot = t.getScopeRoot();
    if (NodeUtil.isFunctionDeclaration(scopeRoot)) {
      
      return scopeRoot.getFirstChild();
    } else {
      Node parent = scopeRoot.getParent();
      if (parent != null) {
        if (parent.getType() == Token.ASSIGN ||
            parent.getLastChild() == scopeRoot &&
            parent.getFirstChild().isQualifiedName()) {
          
          return parent.getFirstChild();
        } else if (parent.getType() == Token.NAME) {
          
          return parent;
        }
      }
    }

    return null;
  }

  
  private void reportBadBaseClassUse(
      NodeTraversal t, Node n, String extraMessage) {
    compiler.report(t.makeError(n, BASE_CLASS_ERROR, extraMessage));
  }

  
  private void processProvideFromPreviousPass(
      NodeTraversal t, String name, Node parent) {
    if (!providedNames.containsKey(name)) {
      
      
      Node expr = new Node(Token.EXPR_RESULT);
      expr.copyInformationFromForTree(parent);
      parent.getParent().addChildBefore(expr, parent);
      compiler.reportCodeChange();

      JSModule module = t.getModule();
      registerAnyProvidedPrefixes(name, expr, module);

      ProvidedName provided = new ProvidedName(name, expr, module, true);
      providedNames.put(name, provided);
      provided.addDefinition(parent, module);
    } else {
      
      
      if (isNamespacePlaceholder(parent)) {
        parent.getParent().removeChild(parent);
        compiler.reportCodeChange();
      }
    }
  }

  
  private void processSetCssNameMapping(NodeTraversal t, Node n, Node parent) {
    Node left = n.getFirstChild();
    Node arg = left.getNext();
    if (verifyArgument(t, left, arg, Token.OBJECTLIT)) {
      
      
      final Map<String, String> cssNames = Maps.newHashMap();
      JSError error = null;
      for (Node key = arg.getFirstChild(); key != null;
          key = key.getNext().getNext()) {
        Node value = key.getNext();
        if (key.getType() != Token.STRING
            || value == null
            || value.getType() != Token.STRING) {
          error = t.makeError(n,
              NON_STRING_PASSED_TO_SET_CSS_NAME_MAPPING_ERROR);
        }
        if (error != null) {
          compiler.report(error);
          break;
        }
        cssNames.put(key.getString(), value.getString());
      }

      
      
      if (error == null) {
        CssRenamingMap cssRenamingMap = new CssRenamingMap() {
          public String get(String value) {
            if (cssNames.containsKey(value)) {
              return cssNames.get(value);
            } else {
              return value;
            }
          }
        };
        compiler.setCssRenamingMap(cssRenamingMap);
        parent.getParent().removeChild(parent);
        compiler.reportCodeChange();
      }
    }
  }

  
  private void trySimplifyNewDate(NodeTraversal t, Node n, Node parent) {
    if (!rewriteNewDateGoogNow) {
      return;
    }
    Preconditions.checkArgument(n.getType() == Token.NEW);
    Node date = n.getFirstChild();
    if (!NodeUtil.isName(date) || !"Date".equals(date.getString())) {
      return;
    }
    Node callGoogNow = date.getNext();
    if (callGoogNow == null || !NodeUtil.isCall(callGoogNow) ||
        callGoogNow.getNext() != null) {
      return;
    }
    Node googNow = callGoogNow.getFirstChild();
    String googNowQName = googNow.getQualifiedName();
    if (googNowQName == null || !"goog.now".equals(googNowQName)
        || googNow.getNext() != null) {
      return;
    }
    n.removeChild(callGoogNow);
    compiler.reportCodeChange();
  }

  
  private boolean verifyProvide(NodeTraversal t, Node methodName, Node arg) {
    if (!verifyArgument(t, methodName, arg)) {
      return false;
    }

    for (String part : arg.getString().split("\\.")) {
      if (!NodeUtil.isValidPropertyName(part)) {
        compiler.report(t.makeError(arg, INVALID_PROVIDE_ERROR, part));
        return false;
      }
    }
    return true;
  }

  
  private boolean verifyArgument(NodeTraversal t, Node methodName, Node arg) {
    return verifyArgument(t, methodName, arg, Token.STRING);
  }

  
  private boolean verifyArgument(NodeTraversal t, Node methodName, Node arg,
      int desiredType) {
    DiagnosticType diagnostic = null;
    if (arg == null) {
      diagnostic = NULL_ARGUMENT_ERROR;
    } else if (arg.getType() != desiredType) {
      diagnostic = INVALID_ARGUMENT_ERROR;
    } else if (arg.getNext() != null) {
      diagnostic = TOO_MANY_ARGUMENTS_ERROR;
    }
    if (diagnostic != null) {
      compiler.report(
          t.makeError(methodName,
              diagnostic, methodName.getQualifiedName()));
      return false;
    }
    return true;
  }

  
  private void registerAnyProvidedPrefixes(
      String ns, Node node, JSModule module) {
    int pos = ns.indexOf('.');
    while (pos != -1) {
      String prefixNs = ns.substring(0, pos);
      pos = ns.indexOf('.', pos + 1);
      if (providedNames.containsKey(prefixNs)) {
        providedNames.get(prefixNs).addProvide(
            node, module, false );
      } else {
        providedNames.put(
            prefixNs,
            new ProvidedName(prefixNs, node, module, false ));
      }
    }
  }

  

  
  private class ProvidedName {
    private final String namespace;

    
    
    private final Node firstNode;
    private final JSModule firstModule;

    
    
    private Node explicitNode = null;
    private JSModule explicitModule = null;

    
    private Node candidateDefinition = null;

    
    private JSModule minimumModule = null;

    
    private Node replacementNode = null;

    ProvidedName(String namespace, Node node, JSModule module,
        boolean explicit) {
      Preconditions.checkArgument(
          node == null  ||
          NodeUtil.isExpressionNode(node));
      this.namespace = namespace;
      this.firstNode = node;
      this.firstModule = module;

      addProvide(node, module, explicit);
    }

    
    void addProvide(Node node, JSModule module, boolean explicit) {
      if (explicit) {
        Preconditions.checkState(explicitNode == null);
        Preconditions.checkArgument(NodeUtil.isExpressionNode(node));
        explicitNode = node;
        explicitModule = module;
      }
      updateMinimumModule(module);
    }

    boolean isExplicitlyProvided() {
      return explicitNode != null;
    }

    
    void addDefinition(Node node, JSModule module) {
      Preconditions.checkArgument(NodeUtil.isExpressionNode(node) || 
                                  NodeUtil.isFunction(node) ||
                                  NodeUtil.isVar(node));
      Preconditions.checkArgument(explicitNode != node);
      if ((candidateDefinition == null) || !NodeUtil.isExpressionNode(node)) {
        candidateDefinition = node;
        updateMinimumModule(module);
      }
    }

    private void updateMinimumModule(JSModule newModule) {
      if (minimumModule == null) {
        minimumModule = newModule;
      } else if (moduleGraph != null) {
        minimumModule = moduleGraph.getDeepestCommonDependencyInclusive(
            minimumModule, newModule);
      } else {
        
        
        Preconditions.checkState(newModule == minimumModule,
                                 "Missing module graph");
      }
    }

    
    void replace() {
      if (firstNode == null) {
        
        replacementNode = candidateDefinition;
        return;
      }

      
      
      if (candidateDefinition != null && explicitNode != null) {
        explicitNode.detachFromParent();
        compiler.reportCodeChange();

        
        replacementNode = candidateDefinition;
        if (NodeUtil.isExpressionNode(candidateDefinition)) {
          candidateDefinition.putBooleanProp(Node.IS_NAMESPACE, true);
          Node assignNode = candidateDefinition.getFirstChild();
          Node nameNode = assignNode.getFirstChild();
          if (nameNode.getType() == Token.NAME) {
            
            Node valueNode = nameNode.getNext();
            assignNode.removeChild(nameNode);
            assignNode.removeChild(valueNode);
            nameNode.addChildToFront(valueNode);
            Node varNode = new Node(Token.VAR, nameNode);
            varNode.copyInformationFrom(candidateDefinition);
            candidateDefinition.getParent().replaceChild(
                candidateDefinition, varNode);
            nameNode.setJSDocInfo(assignNode.getJSDocInfo());
            compiler.reportCodeChange();
            replacementNode = varNode;
          }
        }
      } else {
        
        replacementNode = createDeclarationNode();
        if (firstModule == minimumModule) {
          firstNode.getParent().addChildBefore(replacementNode, firstNode);
        } else {
          
          
          int indexOfDot = namespace.lastIndexOf('.');
          if (indexOfDot == -1) {
            
            compiler.getNodeForCodeInsertion(minimumModule)
                .addChildToBack(replacementNode);
          } else {
            
            ProvidedName parentName =
                providedNames.get(namespace.substring(0, indexOfDot));
            Preconditions.checkNotNull(parentName);
            Preconditions.checkNotNull(parentName.replacementNode);
            parentName.replacementNode.getParent().addChildAfter(
                replacementNode, parentName.replacementNode);
          }
        }
        if (explicitNode != null) {
          explicitNode.detachFromParent();
        }
        compiler.reportCodeChange();
      }
    }

    
    private Node createDeclarationNode() {
      if (namespace.indexOf('.') == -1) {
        return makeVarDeclNode(namespace, firstNode);
      } else {
        return makeAssignmentExprNode(namespace, firstNode);
      }
    }

    
    private Node makeVarDeclNode(String namespace, Node sourceNode) {
      Node name = Node.newString(Token.NAME, namespace);
      name.addChildToFront(createNamespaceLiteral());

      Node decl = new Node(Token.VAR, name);
      decl.putBooleanProp(Node.IS_NAMESPACE, true);

      
      if (compiler.getCodingConvention().isConstant(namespace)) {
        name.putBooleanProp(Node.IS_CONSTANT_NAME, true);
      }

      Preconditions.checkState(isNamespacePlaceholder(decl));
      decl.copyInformationFromForTree(sourceNode);
      return decl;
    }

    
    private Node createNamespaceLiteral() {
      Node objlit = new Node(Token.OBJECTLIT);
      objlit.setJSType(
          compiler.getTypeRegistry().createAnonymousObjectType());
      return objlit;
    }

    
    private Node makeAssignmentExprNode(String namespace, Node node) {
      Node decl = new Node(Token.EXPR_RESULT,
          new Node(Token.ASSIGN,
              NodeUtil.newQualifiedNameNode(namespace, node, namespace),
              createNamespaceLiteral()));
      decl.putBooleanProp(Node.IS_NAMESPACE, true);
      Preconditions.checkState(isNamespacePlaceholder(decl));
      decl.copyInformationFromForTree(node);
      return decl;
    }
  }

  
  private static boolean isNamespacePlaceholder(Node n) {
    if (!n.getBooleanProp(Node.IS_NAMESPACE)) {
      return false;
    }

    Node value = null;
    if (n.getType() == Token.EXPR_RESULT) {
      Node assign = n.getFirstChild();
      value = assign.getLastChild();
    } else if (n.getType() == Token.VAR) {
      Node name = n.getFirstChild();
      value = name.getFirstChild();
    }

    return value != null
      && value.getType() == Token.OBJECTLIT
      && !value.hasChildren();
  }

  

  
  private class UnrecognizedRequire {
    final Node requireNode;
    final String namespace;
    final String inputName;

    UnrecognizedRequire(Node requireNode, String namespace, String inputName) {
      this.requireNode = requireNode;
      this.namespace = namespace;
      this.inputName = inputName;
    }
  }
}

 