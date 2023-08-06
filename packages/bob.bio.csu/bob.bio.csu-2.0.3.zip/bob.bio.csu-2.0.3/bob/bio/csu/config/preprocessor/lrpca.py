import facerec2010
import bob.bio.csu

preprocessor = bob.bio.csu.preprocessor.LRPCA(
    TUNING = facerec2010.baseline.lrpca.GBU_TUNING
)
