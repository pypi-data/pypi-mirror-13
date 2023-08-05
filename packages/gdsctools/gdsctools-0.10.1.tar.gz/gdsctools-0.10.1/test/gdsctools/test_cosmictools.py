from gdsctools.cosmictools import COSMICFetcher, COSMICInfo
from gdsctools.datasets import cosmic_builder_test

def test_cosmic_info():
    c = COSMICInfo()
    assert c.get(930301, 'SAMPLE_NAME') == 'VMRC-MELG'


def test_cosmic_fetcher():
    c = COSMICFetcher(cosmic_builder_test.filename)


def test_cosmic():
    r = COSMICInfo()
    r.get(924100)
    r.get('924100')
    r.get(924100, colname='SAMPLE_NAME')
    r.on_web(924100)
    r.get(1000000000)

