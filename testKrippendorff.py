import sys
from jnius import autoclass

def testUnitizing():
    UAS = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationStudy')
    # raterCount, length
    study = UAS(2, 20)
    # offset, length, rater, category
    study.addUnit(4,2,1, "a")
    study.addUnit(4,2,2, "a")
    study.addUnit(10,3,1, "B")
    study.addUnit(0,3,2, "B")
    KAUA = autoclass('org.dkpro.statistics.agreement.unitizing.KrippendorffAlphaUnitizingAgreement')
    alpha = KAUA(study)
    print(alpha.calculateCategoryAgreement("a"))
    print(alpha.calculateCategoryAgreement("B"))
    UMP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingMatrixPrinter')
    USP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingStudyPrinter')
    ump = UMP()
    System = autoclass('java.lang.System')
    ump.print(System.out, study,  "a", 2, 1)
    ump.print(System.out, study,  "B", 2, 1)
    USP().print(System.out, study)
    USP().printUnitsForCategory(System.out, study, "a", "a")
    USP().printUnitsForCategory(System.out, study, "B", "B")

def testFromPaper():
    # Following matches output from paper:
    # http://anthology.aclweb.org/C/C14/C14-2023.pdf
    CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
    PA = autoclass('org.dkpro.statistics.agreement.coding.PercentageAgreement')
    KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
    NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
    study = CAS(3)
    study.addItemAsArray(["1", "1", "1"])
    study.addItem("1", "2", "2")
    study.addItem("2", "2", "2")
    study.addItem("4", "4", "4")
    study.addItem("1", "4", "4")
    study.addItem("2", "2", "2")
    study.addItem("1", "2", "3")
    study.addItem("3", "3", "3")
    study.addItem("2", "2", "2")
    pa = PA(study)
    print(pa.calculateAgreement())

    alpha = KAA(study, NDF())
    print(alpha.calculateObservedDisagreement())
    print(alpha.calculateExpectedDisagreement())
    print(alpha.calculateAgreement())
    print(alpha.calculateCategoryAgreement("1"))
    print(alpha.calculateCategoryAgreement("2"))
    CMP = autoclass('org.dkpro.statistics.agreement.visualization.CoincidenceMatrixPrinter')
    cmp = CMP()
    System = autoclass('java.lang.System')
    cmp.print(System.out, study)
    RMP = autoclass('org.dkpro.statistics.agreement.visualization.ReliabilityMatrixPrinter')
    RMP().print(System.out, study)

if __name__ == "__main__":
    testUnitizing()
    testFromPaper()
