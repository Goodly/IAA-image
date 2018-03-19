import sys
from jnius import autoclass

CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
PA = autoclass('org.dkpro.statistics.agreement.coding.PercentageAgreement')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
CMP = autoclass('org.dkpro.statistics.agreement.visualization.CoincidenceMatrixPrinter')
RMP = autoclass('org.dkpro.statistics.agreement.visualization.ReliabilityMatrixPrinter')
System = autoclass('java.lang.System')

def makeStudy():
    # Sample data from paper
    # http://anthology.aclweb.org/C/C14/C14-2023.pdf
    # Three raters
    study = CAS(3)
    # Nine items rated
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

def testFromPaper(study):
    # Output numbers match paper
    # http://anthology.aclweb.org/C/C14/C14-2023.pdf
    pa = PA(study)
    print("{:.4f} (percentage agreement)"
          .format(pa.calculateAgreement()))

    alpha = KAA(study, NDF())
    print("{:.4f} (observed disagreement)"
          .format(alpha.calculateObservedDisagreement()))
    print("{:.4f} (expected disagreement)"
          .format(alpha.calculateExpectedDisagreement()))
    print("{:.4f} (α coefficient)"
          .format(alpha.calculateAgreement()))
    print("{:.4f} (Categtory 1 α)"
          .format(alpha.calculateCategoryAgreement("1")))
    print("{:.4f} (Categtory 2 α)"
          .format(alpha.calculateCategoryAgreement("2")))
    print("Coincidence Matrix")
    cmp = CMP()
    cmp.print(System.out, study)

def testRMP(study):
    print("Reliability Matrix")
    RMP().print(System.out, study)

if __name__ == "__main__":
    study = makeStudy()
    testFromPaper(study)
    testRMP(study)
