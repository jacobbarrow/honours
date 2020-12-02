from scipy.stats import mannwhitneyu
from scipy.stats import ttest_ind
from scipy.stats import shapiro


def calcSignificance(set1, set2):
    _, p = shapiro(set1)

    if p > 0.05:  # Guassian - use t-test
        distribution = "Gaussian"
        _, p2 = ttest_ind(set1, set2)

    else:  # Non-gaussian - use mwu
        distribution = "not Gaussian"
        _, p2 = mannwhitneyu(set1, set2)

    return {'p': p2, 'distribution': distribution}
