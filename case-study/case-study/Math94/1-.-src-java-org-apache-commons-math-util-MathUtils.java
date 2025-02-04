

package org.apache.commons.math.util;

import java.math.BigDecimal;
import java.util.Arrays;


public final class MathUtils {

    
    public static final double EPSILON = 0x1.0p-53;

    
    public static final double SAFE_MIN = 0x1.0p-1022;

    
    private static final byte  NB = (byte)-1;

    
    private static final short NS = (short)-1;

    
    private static final byte  PB = (byte)1;

    
    private static final short PS = (short)1;

    
    private static final byte  ZB = (byte)0;

    
    private static final short ZS = (short)0;

    
    private static final double TWO_PI = 2 * Math.PI;

    
    private MathUtils() {
        super();
    }

    
    public static int addAndCheck(int x, int y) {
        long s = (long)x + (long)y;
        if (s < Integer.MIN_VALUE || s > Integer.MAX_VALUE) {
            throw new ArithmeticException("overflow: add");
        }
        return (int)s;
    }

    
    public static long addAndCheck(long a, long b) {
        return addAndCheck(a, b, "overflow: add");
    }
    
    
    private static long addAndCheck(long a, long b, String msg) {
        long ret;
        if (a > b) {
            
            ret = addAndCheck(b, a, msg);
        } else {
            
            
            if (a < 0) {
                if (b < 0) {
                    
                    if (Long.MIN_VALUE - b <= a) {
                        ret = a + b;
                    } else {
                        throw new ArithmeticException(msg);
                    }
                } else {
                    
                    ret = a + b;
                }
            } else {
                
                

                
                if (a <= Long.MAX_VALUE - b) {
                    ret = a + b;
                } else {
                    throw new ArithmeticException(msg);
                }
            }
        }
        return ret;
    }
    
    
    public static long binomialCoefficient(final int n, final int k) {
        if (n < k) {
            throw new IllegalArgumentException(
                "must have n >= k for binomial coefficient (n,k)");
        }
        if (n < 0) {
            throw new IllegalArgumentException(
                "must have n >= 0 for binomial coefficient (n,k)");
        }
        if ((n == k) || (k == 0)) {
            return 1;
        }
        if ((k == 1) || (k == n - 1)) {
            return n;
        }

        long result = Math.round(binomialCoefficientDouble(n, k));
        if (result == Long.MAX_VALUE) {
            throw new ArithmeticException(
                "result too large to represent in a long integer");
        }
        return result;
    }

    
    public static double binomialCoefficientDouble(final int n, final int k) {
        return Math.floor(Math.exp(binomialCoefficientLog(n, k)) + 0.5);
    }
    
    
    public static double binomialCoefficientLog(final int n, final int k) {
        if (n < k) {
            throw new IllegalArgumentException(
                "must have n >= k for binomial coefficient (n,k)");
        }
        if (n < 0) {
            throw new IllegalArgumentException(
                "must have n >= 0 for binomial coefficient (n,k)");
        }
        if ((n == k) || (k == 0)) {
            return 0;
        }
        if ((k == 1) || (k == n - 1)) {
            return Math.abs((double)n);
        }
        double logSum = 0;

        
        for (int i = k + 1; i <= n; i++) {
            logSum += Math.log((double)i);
        }

        
        for (int i = 2; i <= n - k; i++) {
            logSum -= Math.log((double)i);
        }

        return logSum;
    }
    
    
    public static double cosh(double x) {
        return (Math.exp(x) + Math.exp(-x)) / 2.0;
    }
    
    
    public static boolean equals(double x, double y) {
        return ((Double.isNaN(x) && Double.isNaN(y)) || x == y);
    }

    
    public static boolean equals(double[] x, double[] y) {
        if ((x == null) || (y == null)) {
            return !((x == null) ^ (y == null));
        }
        if (x.length != y.length) {
            return false;
        }
        for (int i = 0; i < x.length; ++i) {
            if (!equals(x[i], y[i])) {
                return false;
            }
        }
        return true;
    }

    
    public static long factorial(final int n) {
        long result = Math.round(factorialDouble(n));
        if (result == Long.MAX_VALUE) {
            throw new ArithmeticException(
                "result too large to represent in a long integer");
        }
        return result;
    }

    
    public static double factorialDouble(final int n) {
        if (n < 0) {
            throw new IllegalArgumentException("must have n >= 0 for n!");
        }
        return Math.floor(Math.exp(factorialLog(n)) + 0.5);
    }

    
    public static double factorialLog(final int n) {
        if (n < 0) {
            throw new IllegalArgumentException("must have n > 0 for n!");
        }
        double logSum = 0;
        for (int i = 2; i <= n; i++) {
            logSum += Math.log((double)i);
        }
        return logSum;
    }

    
    public static int gcd(int u, int v) {
        if ((u == 0) || (v == 0)) {
            return (Math.abs(u) + Math.abs(v));
        }
        
        
        
        
        
        if (u > 0) {
            u = -u;
        } 
        if (v > 0) {
            v = -v;
        } 
        
        int k = 0;
        while ((u & 1) == 0 && (v & 1) == 0 && k < 31) { 
                                                            
            u /= 2;
            v /= 2;
            k++; 
        }
        if (k == 31) {
            throw new ArithmeticException("overflow: gcd is 2^31");
        }
        
        
        int t = ((u & 1) == 1) ? v : -(u / 2);
        
        
        do {
            
            
            while ((t & 1) == 0) { 
                t /= 2; 
            }
            
            if (t > 0) {
                u = -t;
            } else {
                v = t;
            }
            
            t = (v - u) / 2;
            
            
        } while (t != 0);
        return -u * (1 << k); 
    }

    
    public static int hash(double value) {
        return new Double(value).hashCode();
    }

    
    public static int hash(double[] value) {
        return Arrays.hashCode(value);
    }

    
    public static byte indicator(final byte x) {
        return (x >= ZB) ? PB : NB;
    }

    
    public static double indicator(final double x) {
        if (Double.isNaN(x)) {
            return Double.NaN;
        }
        return (x >= 0.0) ? 1.0 : -1.0;
    }

    
    public static float indicator(final float x) {
        if (Float.isNaN(x)) {
            return Float.NaN;
        }
        return (x >= 0.0F) ? 1.0F : -1.0F;
    }

    
    public static int indicator(final int x) {
        return (x >= 0) ? 1 : -1;
    }

    
    public static long indicator(final long x) {
        return (x >= 0L) ? 1L : -1L;
    }

    
    public static short indicator(final short x) {
        return (x >= ZS) ? PS : NS;
    }

    
    public static int lcm(int a, int b) {
        return Math.abs(mulAndCheck(a / gcd(a, b), b));
    }

     
    public static double log(double base, double x) {
        return Math.log(x)/Math.log(base);
    }

    
    public static int mulAndCheck(int x, int y) {
        long m = ((long)x) * ((long)y);
        if (m < Integer.MIN_VALUE || m > Integer.MAX_VALUE) {
            throw new ArithmeticException("overflow: mul");
        }
        return (int)m;
    }

    
    public static long mulAndCheck(long a, long b) {
        long ret;
        String msg = "overflow: multiply";
        if (a > b) {
            
            ret = mulAndCheck(b, a);
        } else {
            if (a < 0) {
                if (b < 0) {
                    
                    if (a >= Long.MAX_VALUE / b) {
                        ret = a * b;
                    } else {
                        throw new ArithmeticException(msg);
                    }
                } else if (b > 0) {
                    
                    if (Long.MIN_VALUE / b <= a) {
                        ret = a * b;
                    } else {
                        throw new ArithmeticException(msg);
                        
                    }
                } else {
                    
                    ret = 0;
                }
            } else if (a > 0) {
                
                
                
                
                if (a <= Long.MAX_VALUE / b) {
                    ret = a * b;
                } else {
                    throw new ArithmeticException(msg);
                }
            } else {
                
                ret = 0;
            }
        }
        return ret;
    }

    
    public static double nextAfter(double d, double direction) {

        
        if (Double.isNaN(d) || Double.isInfinite(d)) {
                return d;
        } else if (d == 0) {
                return (direction < 0) ? -Double.MIN_VALUE : Double.MIN_VALUE;
        }
        
        

        
        long bits     = Double.doubleToLongBits(d);
        long sign     = bits & 0x8000000000000000L;
        long exponent = bits & 0x7ff0000000000000L;
        long mantissa = bits & 0x000fffffffffffffL;

        if (d * (direction - d) >= 0) {
                
                if (mantissa == 0x000fffffffffffffL) {
                        return Double.longBitsToDouble(sign |
                                        (exponent + 0x0010000000000000L));
                } else {
                        return Double.longBitsToDouble(sign |
                                        exponent | (mantissa + 1));
                }
        } else {
                
                if (mantissa == 0L) {
                        return Double.longBitsToDouble(sign |
                                        (exponent - 0x0010000000000000L) |
                                        0x000fffffffffffffL);
                } else {
                        return Double.longBitsToDouble(sign |
                                        exponent | (mantissa - 1));
                }
        }

    }

    
    public static double scalb(final double d, final int scaleFactor) {

        
        if ((d == 0) || Double.isNaN(d) || Double.isInfinite(d)) {
            return d;
        }

        
        final long bits     = Double.doubleToLongBits(d);
        final long exponent = bits & 0x7ff0000000000000L;
        final long rest     = bits & 0x800fffffffffffffL;

        
        final long newBits = rest | (exponent + (((long) scaleFactor) << 52));
        return Double.longBitsToDouble(newBits);

    }

    
     public static double normalizeAngle(double a, double center) {
         return a - TWO_PI * Math.floor((a + Math.PI - center) / TWO_PI);
     }

    
    public static double round(double x, int scale) {
        return round(x, scale, BigDecimal.ROUND_HALF_UP);
    }

    
    public static double round(double x, int scale, int roundingMethod) {
        try {
            return (new BigDecimal
                   (Double.toString(x))
                   .setScale(scale, roundingMethod))
                   .doubleValue();
        } catch (NumberFormatException ex) {
            if (Double.isInfinite(x)) {
                return x;          
            } else {
                return Double.NaN;
            }
        }
    }

    
    public static float round(float x, int scale) {
        return round(x, scale, BigDecimal.ROUND_HALF_UP);
    }

    
    public static float round(float x, int scale, int roundingMethod) {
        float sign = indicator(x);
        float factor = (float)Math.pow(10.0f, scale) * sign;
        return (float)roundUnscaled(x * factor, sign, roundingMethod) / factor;
    }

    
    private static double roundUnscaled(double unscaled, double sign,
        int roundingMethod) {
        switch (roundingMethod) {
        case BigDecimal.ROUND_CEILING :
            if (sign == -1) {
                unscaled = Math.floor(nextAfter(unscaled, Double.NEGATIVE_INFINITY));
            } else {
                unscaled = Math.ceil(nextAfter(unscaled, Double.POSITIVE_INFINITY));
            }
            break;
        case BigDecimal.ROUND_DOWN :
            unscaled = Math.floor(nextAfter(unscaled, Double.NEGATIVE_INFINITY));
            break;
        case BigDecimal.ROUND_FLOOR :
            if (sign == -1) {
                unscaled = Math.ceil(nextAfter(unscaled, Double.POSITIVE_INFINITY));
            } else {
                unscaled = Math.floor(nextAfter(unscaled, Double.NEGATIVE_INFINITY));
            }
            break;
        case BigDecimal.ROUND_HALF_DOWN : {
            unscaled = nextAfter(unscaled, Double.NEGATIVE_INFINITY);
            double fraction = unscaled - Math.floor(unscaled);
            if (fraction > 0.5) {
                unscaled = Math.ceil(unscaled);
            } else {
                unscaled = Math.floor(unscaled);
            }
            break;
        }
        case BigDecimal.ROUND_HALF_EVEN : {
            double fraction = unscaled - Math.floor(unscaled);
            if (fraction > 0.5) {
                unscaled = Math.ceil(unscaled);
            } else if (fraction < 0.5) {
                unscaled = Math.floor(unscaled);
            } else {
                
                if (Math.floor(unscaled) / 2.0 == Math.floor(Math
                    .floor(unscaled) / 2.0)) { 
                    unscaled = Math.floor(unscaled);
                } else { 
                    unscaled = Math.ceil(unscaled);
                }
            }
            break;
        }
        case BigDecimal.ROUND_HALF_UP : {
            unscaled = nextAfter(unscaled, Double.POSITIVE_INFINITY);
            double fraction = unscaled - Math.floor(unscaled);
            if (fraction >= 0.5) {
                unscaled = Math.ceil(unscaled);
            } else {
                unscaled = Math.floor(unscaled);
            }
            break;
        }
        case BigDecimal.ROUND_UNNECESSARY :
            if (unscaled != Math.floor(unscaled)) {
                throw new ArithmeticException("Inexact result from rounding");
            }
            break;
        case BigDecimal.ROUND_UP :
            unscaled = Math.ceil(nextAfter(unscaled,  Double.POSITIVE_INFINITY));
            break;
        default :
            throw new IllegalArgumentException("Invalid rounding method.");
        }
        return unscaled;
    }

    
    public static byte sign(final byte x) {
        return (x == ZB) ? ZB : (x > ZB) ? PB : NB;
    }

    
    public static double sign(final double x) {
        if (Double.isNaN(x)) {
            return Double.NaN;
        }
        return (x == 0.0) ? 0.0 : (x > 0.0) ? 1.0 : -1.0;
    }

    
    public static float sign(final float x) {
        if (Float.isNaN(x)) {
            return Float.NaN;
        }
        return (x == 0.0F) ? 0.0F : (x > 0.0F) ? 1.0F : -1.0F;
    }

    
    public static int sign(final int x) {
        return (x == 0) ? 0 : (x > 0) ? 1 : -1;
    }

    
    public static long sign(final long x) {
        return (x == 0L) ? 0L : (x > 0L) ? 1L : -1L;
    }

    
    public static short sign(final short x) {
        return (x == ZS) ? ZS : (x > ZS) ? PS : NS;
    }

    
    public static double sinh(double x) {
        return (Math.exp(x) - Math.exp(-x)) / 2.0;
    }

    
    public static int subAndCheck(int x, int y) {
        long s = (long)x - (long)y;
        if (s < Integer.MIN_VALUE || s > Integer.MAX_VALUE) {
            throw new ArithmeticException("overflow: subtract");
        }
        return (int)s;
    }

    
    public static long subAndCheck(long a, long b) {
        long ret;
        String msg = "overflow: subtract";
        if (b == Long.MIN_VALUE) {
            if (a < 0) {
                ret = a - b;
            } else {
                throw new ArithmeticException(msg);
            }
        } else {
            
            ret = addAndCheck(a, -b, msg);
        }
        return ret;
    }

}

 