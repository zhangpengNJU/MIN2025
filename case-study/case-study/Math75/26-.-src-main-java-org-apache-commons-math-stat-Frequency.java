
package org.apache.commons.math.stat;

import java.io.Serializable;
import java.text.NumberFormat;
import java.util.Iterator;
import java.util.Comparator;
import java.util.TreeMap;

import org.apache.commons.math.MathRuntimeException;


public class Frequency implements Serializable {

    
    private static final long serialVersionUID = -3845586908418844111L;

    
    private final TreeMap<Comparable<?>, Long> freqTable;

    
    public Frequency() {
        freqTable = new TreeMap<Comparable<?>, Long>();
    }

    
    @SuppressWarnings("unchecked")
    public Frequency(Comparator<?> comparator) {
        freqTable = new TreeMap<Comparable<?>, Long>((Comparator<? super Comparable<?>>) comparator);
    }

    
    @Override
    public String toString() {
        NumberFormat nf = NumberFormat.getPercentInstance();
        StringBuffer outBuffer = new StringBuffer();
        outBuffer.append("Value \t Freq. \t Pct. \t Cum Pct. \n");
        Iterator<Comparable<?>> iter = freqTable.keySet().iterator();
        while (iter.hasNext()) {
            Comparable<?> value = iter.next();
            outBuffer.append(value);
            outBuffer.append('\t');
            outBuffer.append(getCount(value));
            outBuffer.append('\t');
            outBuffer.append(nf.format(getPct(value)));
            outBuffer.append('\t');
            outBuffer.append(nf.format(getCumPct(value)));
            outBuffer.append('\n');
        }
        return outBuffer.toString();
    }

    
    @Deprecated
    public void addValue(Object v) {
        if (v instanceof Comparable<?>){
            addValue((Comparable<?>) v);
        } else {
            throw MathRuntimeException.createIllegalArgumentException(
                  "class ({0}) does not implement Comparable",
                  v.getClass().getName());
        }
    }

    
    public void addValue(Comparable<?> v){
        Comparable<?> obj = v;
        if (v instanceof Integer) {
           obj = Long.valueOf(((Integer) v).longValue());
        }
        try {
            Long count = freqTable.get(obj);
            if (count == null) {
                freqTable.put(obj, Long.valueOf(1));
            } else {
                freqTable.put(obj, Long.valueOf(count.longValue() + 1));
            }
        } catch (ClassCastException ex) {
            
            throw MathRuntimeException.createIllegalArgumentException(
                  "instance of class {0} not comparable to existing values",
                  v.getClass().getName());
        }
    }

    
    public void addValue(int v) {
        addValue(Long.valueOf(v));
    }

    
    public void addValue(Integer v) {
        addValue(Long.valueOf(v.longValue()));
    }

    
    public void addValue(long v) {
        addValue(Long.valueOf(v));
    }

    
    public void addValue(char v) {
        addValue(Character.valueOf(v));
    }

    
    public void clear() {
        freqTable.clear();
    }

    
    public Iterator<Comparable<?>> valuesIterator() {
        return freqTable.keySet().iterator();
    }

    

    
    public long getSumFreq() {
        long result = 0;
        Iterator<Long> iterator = freqTable.values().iterator();
        while (iterator.hasNext())  {
            result += iterator.next().longValue();
        }
        return result;
    }

    
    @Deprecated
    public long getCount(Object v) {
        return getCount((Comparable<?>) v);
    }

    
    public long getCount(Comparable<?> v) {
        if (v instanceof Integer) {
            return getCount(((Integer) v).longValue());
        }
        long result = 0;
        try {
            Long count =  freqTable.get(v);
            if (count != null) {
                result = count.longValue();
            }
        } catch (ClassCastException ex) {
            
        }
        return result;
    }

    
    public long getCount(int v) {
        return getCount(Long.valueOf(v));
    }

    
    public long getCount(long v) {
        return getCount(Long.valueOf(v));
    }

    
    public long getCount(char v) {
        return getCumFreq(Character.valueOf(v));
    }

    

    
    @Deprecated
    public double getPct(Object v) {
        return getPct((Comparable<?>) v);
    }

    
    public double getPct(Comparable<?> v) {
        final long sumFreq = getSumFreq();
        if (sumFreq == 0) {
            return Double.NaN;
        }
        return (double) getCount(v) / (double) sumFreq;
    }

    
    public double getPct(int v) {
        return getPct(Long.valueOf(v));
    }

    
    public double getPct(long v) {
        return getPct(Long.valueOf(v));
    }

    
    public double getPct(char v) {
        return getPct(Character.valueOf(v));
    }

    

    
    @Deprecated
    public long getCumFreq(Object v) {
        return getCumFreq((Comparable<?>) v);
    }

    
    @SuppressWarnings("unchecked")
        public long getCumFreq(Comparable<?> v) {
        if (getSumFreq() == 0) {
            return 0;
        }
        if (v instanceof Integer) {
            return getCumFreq(((Integer) v).longValue());
        }
        Comparator<Comparable<?>> c = (Comparator<Comparable<?>>) freqTable.comparator();
        if (c == null) {
            c = new NaturalComparator();
        }
        long result = 0;

        try {
            Long value = freqTable.get(v);
            if (value != null) {
                result = value.longValue();
            }
        } catch (ClassCastException ex) {
            return result;   
        }

        if (c.compare(v, freqTable.firstKey()) < 0) {
            return 0;  
        }

        if (c.compare(v, freqTable.lastKey()) >= 0) {
            return getSumFreq();    
        }

        Iterator<Comparable<?>> values = valuesIterator();
        while (values.hasNext()) {
            Comparable<?> nextValue = values.next();
            if (c.compare(v, nextValue) > 0) {
                result += getCount(nextValue);
            } else {
                return result;
            }
        }
        return result;
    }

     
    public long getCumFreq(int v) {
        return getCumFreq(Long.valueOf(v));
    }

     
    public long getCumFreq(long v) {
        return getCumFreq(Long.valueOf(v));
    }

    
    public long getCumFreq(char v) {
        return getCumFreq(Character.valueOf(v));
    }

    

    
    @Deprecated
    public double getCumPct(Object v) {
        return getCumPct((Comparable<?>) v);

    }

    
    public double getCumPct(Comparable<?> v) {
        final long sumFreq = getSumFreq();
        if (sumFreq == 0) {
            return Double.NaN;
        }
        return (double) getCumFreq(v) / (double) sumFreq;
    }

    
    public double getCumPct(int v) {
        return getCumPct(Long.valueOf(v));
    }

    
    public double getCumPct(long v) {
        return getCumPct(Long.valueOf(v));
    }

    
    public double getCumPct(char v) {
        return getCumPct(Character.valueOf(v));
    }

    
    private static class NaturalComparator<T extends Comparable<T>> implements Comparator<Comparable<T>>, Serializable {

        
        private static final long serialVersionUID = -3852193713161395148L;

        
        @SuppressWarnings("unchecked")
        public int compare(Comparable<T> o1, Comparable<T> o2) {
            return o1.compareTo((T) o2);
        }
    }

    
    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result +
                 ((freqTable == null) ? 0 : freqTable.hashCode());
        return result;
    }

    
    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (!(obj instanceof Frequency))
            return false;
        Frequency other = (Frequency) obj;
        if (freqTable == null) {
            if (other.freqTable != null)
                return false;
        } else if (!freqTable.equals(other.freqTable))
            return false;
        return true;
    }

}

 