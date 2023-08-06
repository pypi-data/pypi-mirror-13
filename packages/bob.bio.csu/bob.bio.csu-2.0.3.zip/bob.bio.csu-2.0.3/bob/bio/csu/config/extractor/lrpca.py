import facerec2010
import bob.bio.csu

extractor = bob.bio.csu.extractor.LRPCA(
    TUNING = facerec2010.baseline.lrpca.GBU_TUNING
)
