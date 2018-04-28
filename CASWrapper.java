import de.tudarmstadt.ukp.dkpro.statistics.agreement.coding.CodingAnnotationStudy;



public class CASWrapper {
    public static CodingAnnotationStudy makeStudy(int[] input){
        Integer[] bigIInput = new Integer[input.length];
        for (int i = 0; i< input.length; i+=1){
            Integer member = new Integer(input[i]);
            bigIInput[i] = member;
        }
        CodingAnnotationStudy study = new CodingAnnotationStudy(input.length);
        study.addItemAsArray(bigIInput);
        return study;
    }

}
