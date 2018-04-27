import sys
from jnius import autoclass

CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
PA = autoclass('org.dkpro.statistics.agreement.coding.PercentageAgreement')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')
IDF = autoclass('org.dkpro.statistics.agreement.distance.IntervalDistanceFunction')
CMP = autoclass('org.dkpro.statistics.agreement.visualization.CoincidenceMatrixPrinter')
RMP = autoclass('org.dkpro.statistics.agreement.visualization.ReliabilityMatrixPrinter')
System = autoclass('java.lang.System')
Integer = autoclass('java.lang.Integer')

def testDistances(study):
    # https://docs.oracle.com/javase/tutorial/java/data/autoboxing.html
    # Box
    a = Integer(8)
    print(a) # horrible class name output
    # Unbox
    print(a.intValue()) # 8

    ndf = NDF()
    print("{} nominal distance".format(ndf.measureDistance(study, Integer(1), Integer(1))))
    print("{} nominal distance".format(ndf.measureDistance(study, Integer(1), Integer(2))))
    print("{} nominal distance".format(ndf.measureDistance(study, Integer(1), Integer(3))))
    odf = ODF()
    print("{} ordinal distance".format(odf.measureDistance(study, Integer(1), Integer(1))))
    print("{} ordinal distance".format(odf.measureDistance(study, Integer(1), Integer(2))))
    print("{} ordinal distance".format(odf.measureDistance(study, Integer(1), Integer(3))))
    idf = IDF()
    print("{} interval distance".format(idf.measureDistance(study, Integer(1), Integer(1))))
    print("{} interval distance".format(idf.measureDistance(study, Integer(1), Integer(2))))
    print("{} interval distance".format(idf.measureDistance(study, Integer(1), Integer(3))))

def makeStringStudy():
    # Sample data from paper
    # http://anthology.aclweb.org/C/C14/C14-2023.pdf
    # Three raters
    # Nine items rated
    study = CAS(3)
    study.addItemAsArray(["1", "1", "1"])
    study.addItemAsArray(["1", "2", "2"])
    study.addItemAsArray(["2", "2", "2"])
    study.addItemAsArray(["4", "4", "4"])
    study.addItemAsArray(["1", "4", "4"])
    study.addItemAsArray(["2", "2", "2"])
    study.addItemAsArray(["1", "2", "3"])
    study.addItemAsArray(["3", "3", "3"])
    study.addItemAsArray(["2", "2", "2"])
    return study

def makeIntegerStudy():
    study = CAS(3)
    study.addItemAsArray([Integer(1), Integer(1), Integer(1)])
    study.addItemAsArray([Integer(1), Integer(2), Integer(2)])
    study.addItemAsArray([Integer(2), Integer(2), Integer(2)])
    study.addItemAsArray([Integer(4), Integer(4), Integer(4)])
    study.addItemAsArray([Integer(1), Integer(4), Integer(4)])
    study.addItemAsArray([Integer(2), Integer(2), Integer(2)])
    study.addItemAsArray([Integer(1), Integer(2), Integer(3)])
    study.addItemAsArray([Integer(3), Integer(3), Integer(3)])
    study.addItemAsArray([Integer(2), Integer(2), Integer(2)])
    return study

def testFromPaper(study, df):
    # Output numbers match paper
    # http://anthology.aclweb.org/C/C14/C14-2023.pdf
    print("----")
    pa = PA(study)
    print("{:.4f} (percentage agreement)"
          .format(pa.calculateAgreement()))

    alpha = KAA(study, df)
    print("{:.4f} (observed disagreement)"
          .format(alpha.calculateObservedDisagreement()))
    print("{:.4f} (expected disagreement)"
          .format(alpha.calculateExpectedDisagreement()))
    print("{:.4f} (α coefficient)"
          .format(alpha.calculateAgreement()))
    print("{:.4f} (Categtory 1 α)"
          .format(alpha.calculateCategoryAgreement(Integer(1))))
    print("{:.4f} (Categtory 2 α)"
          .format(alpha.calculateCategoryAgreement(Integer(2))))
    print("Coincidence Matrix")
    cmp = CMP()
    cmp.print(System.out, study)

def testRMP(study):
    print("Reliability Matrix")
    RMP().print(System.out, study)

if __name__ == "__main__":
    study = makeStringStudy()
    testFromPaper(study, NDF())
    int_study = makeIntegerStudy()
    testFromPaper(int_study, NDF())
    testFromPaper(int_study, ODF())
    testFromPaper(int_study, IDF())
    testRMP(study)
    testDistances(int_study)
