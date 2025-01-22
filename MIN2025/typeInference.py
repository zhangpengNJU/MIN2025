import javalang

codestr='''

/* ===========================================================
 * JFreeChart : a free chart library for the Java(tm) platform
 * ===========================================================
 *
 * (C) Copyright 2000-2009, by Object Refinery Limited and Contributors.
 *
 * Project Info:  http://www.jfree.org/jfreechart/index.html
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
 * USA.
 *
 * [Java is a trademark or registered trademark of Sun Microsystems, Inc.
 * in the United States and other countries.]
 *
 * ------------------
 * BarChartDemo1.java
 * ------------------
 * (C) Copyright 2003-2009, by Object Refinery Limited and Contributors.
 *
 * Original Author:  David Gilbert (for Object Refinery Limited);
 * Contributor(s):   ;
 *
 * Changes
 * -------
 * 09-Mar-2005 : Version 1 (DG);
 * 21-Jun-2007 : Removed JCommon dependencies (DG);
 *
 */

package org.jfree.chart.demo;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.GradientPaint;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.CategoryLabelPositions;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.chart.util.ApplicationFrame;
import org.jfree.chart.util.RefineryUtilities;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.category.DefaultCategoryDataset;

/**
 * A simple demonstration application showing how to create a bar chart.
 */
public class BarChartDemo1 extends ApplicationFrame {

    /**
     * Creates a new demo instance.
     *
     * @param title  the frame title.
     */
    public BarChartDemo1(String title) {
        super(title);
        CategoryDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setFillZoomRectangle(true);
        chartPanel.setMouseWheelEnabled(true);
        chartPanel.setPreferredSize(new Dimension(500, 270));
        setContentPane(chartPanel);
    }

    /**
     * Returns a sample dataset.
     *
     * @return The dataset.
     */
    private static CategoryDataset createDataset() {

        // row keys...
        String series1 = "First";
        String series2 = "Second";
        String series3 = "Third";

        // column keys...
        String category1 = "Category 1";
        String category2 = "Category 2";
        String category3 = "Category 3";
        String category4 = "Category 4";
        String category5 = "Category 5";

        // create the dataset...
        DefaultCategoryDataset dataset = new DefaultCategoryDataset();

        dataset.addValue(1.0, series1, category1);
        dataset.addValue(4.0, series1, category2);
        dataset.addValue(3.0, series1, category3);
        dataset.addValue(5.0, series1, category4);
        dataset.addValue(5.0, series1, category5);

        dataset.addValue(5.0, series2, category1);
        dataset.addValue(7.0, series2, category2);
        dataset.addValue(6.0, series2, category3);
        dataset.addValue(8.0, series2, category4);
        dataset.addValue(4.0, series2, category5);

        dataset.addValue(4.0, series3, category1);
        dataset.addValue(3.0, series3, category2);
        dataset.addValue(2.0, series3, category3);
        dataset.addValue(3.0, series3, category4);
        dataset.addValue(6.0, series3, category5);

        return dataset;

    }

    /**
     * Creates a sample chart.
     *
     * @param dataset  the dataset.
     *
     * @return The chart.
     */
    private static JFreeChart createChart(CategoryDataset dataset) {

        JFreeChart chart = ChartFactory.createBarChart("Bar Chart Demo 1",
                "Category", "Value", dataset, true);                   
        CategoryPlot plot = (CategoryPlot) chart.getPlot();

        // ******************************************************************
        //  More than 150 demo applications are included with the JFreeChart
        //  Developer Guide...for more information, see:
        //
        //  >   http://www.object-refinery.com/jfreechart/guide.html
        //
        // ******************************************************************

        // set the range axis to display integers only...
        NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());

        // disable bar outlines...
        BarRenderer renderer = (BarRenderer) plot.getRenderer();
        renderer.setDrawBarOutline(false);

        // set up gradient paints for series...
        GradientPaint gp0 = new GradientPaint(0.0f, 0.0f, Color.blue,
                0.0f, 0.0f, new Color(0, 0, 64));
        GradientPaint gp1 = new GradientPaint(0.0f, 0.0f, Color.green,
                0.0f, 0.0f, new Color(0, 64, 0));
        GradientPaint gp2 = new GradientPaint(0.0f, 0.0f, Color.red,
                0.0f, 0.0f, new Color(64, 0, 0));
        renderer.setSeriesPaint(0, gp0);
        renderer.setSeriesPaint(1, gp1);
        renderer.setSeriesPaint(2, gp2);

        CategoryAxis domainAxis = plot.getDomainAxis();
        domainAxis.setCategoryLabelPositions(
                CategoryLabelPositions.createUpRotationLabelPositions(
                        Math.PI / 6.0));

        return chart;

    }

    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {
        BarChartDemo1 demo = new BarChartDemo1("Bar Chart Demo 1");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);
    }

}
'''

'''
public class Clazz{
    private static DateFormat format = new SimpleDateFormat("yyyy/MM/dd");
    public int i=53;

    public Date method(String date){
        int i=53;
        DateFormat format2 = new SimpleDateFormat("yyyy/MM/dd");
        return format.parse(date);
    }
}'''

#tree = javalang.parse.parse(codestr)

x=1

'''
#可以找到所有带type的节点
for path, node in tree.filter(javalang.tree.Type):
    #对于classcreater，不用管，它可能没有对应的名字
    if type(path[-1])==javalang.tree.ClassCreator:
        print("no name")
    #方法定义时的类型，也可以不管，只有在A.x().B()中，对B进行变异时，才需要分析A.x()的类型。分析A的类型并变异x即可。
    elif type(path[-1])==javalang.tree.MethodDeclaration:
        print("continue")
    elif type(path[-1])==javalang.tree.FormalParameter:
        print(path[-1].name)
    else:
        print(path[-1].declarators[0].name)
    #x=path[-1]
    #print(path[-1])
    #print(node.name)
'''
'''
for path, node in tree.filter(javalang.tree.Type):
    #对于classcreater，不用管，它可能没有对应的名字
    print(node.name)
    if type(path[-1])==javalang.tree.ClassDeclaration:
        break
'''



#返回一个dic， dic[id]={typeset}，dic【名字】={类型集合}
def typeInferenceForCode(codestr):
    tree=javalang.parse.parse(codestr)
    dic={}
    for path, node in tree.filter(javalang.tree.Type):
        # 对于classcreater，不用管，它可能没有对应的名字
        if type(path[-1]) == javalang.tree.ClassCreator:
            a=1
            #print("no name")
        # 方法定义时的类型，也可以不管，只有在A.x().B()中，对B进行变异时，才需要分析A.x()的类型。分析A的类型并变异x即可。
        elif type(path[-1]) == javalang.tree.MethodDeclaration:
            a=1
            #print("continue")
        elif type(path[-1]) == javalang.tree.Cast:
            a=1
            #print("continue")
        elif hasattr(path[-1],"name"):
        #elif type(path[-1]) == javalang.tree.FormalParameter:
            if path[-1].name in dic:
                dic[path[-1].name]={node.name}|dic[path[-1].name]
            else:
                dic[path[-1].name]={node.name}
            #print(path[-1].name)
        elif hasattr(path[-1],"declarators"):
            if path[-1].declarators[0].name in dic:
                dic[path[-1].declarators[0].name]={node.name}|dic[path[-1].declarators[0].name]
            else:
                dic[path[-1].declarators[0].name]={node.name}
            #print(path[-1].declarators[0].name)
    return dic

