import org.dkpro.statistics.agreement.coding.CodingAnnotationStudy;

public class CASWrapper extends CodingAnnotationStudy {
    public CASWrapper(int raterCount) {
      super(raterCount);
    }

    public void addAsArray(int[] input){
        Integer[] bigIInput = new Integer[input.length];
        for (int i = 0; i< input.length; i+=1){
            Integer member = new Integer(input[i]);
            bigIInput[i] = member;
        }
        this.addItemAsArray(bigIInput);
    }
}
