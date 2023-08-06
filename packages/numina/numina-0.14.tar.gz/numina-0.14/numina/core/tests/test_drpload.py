
import pytest
import pkgutil

from ..pipeline import DrpSystem


def test_drpsys_one_instrument(drpmocker):
    """Test that only one DRP is returned."""

    drpdata1 = pkgutil.get_data('numina.core.tests', 'drpfake1.yaml')

    drpmocker.add_drp('FAKE1', drpdata1)

    drpsys = DrpSystem()

    ldrp = drpsys.query_by_name('FAKE1')

    assert ldrp is not None
    assert ldrp.name == 'FAKE1'

    ldrp2 = drpsys.query_by_name('OTHER')
    assert ldrp2 is None

    alldrps = drpsys.query_all()
    assert len(alldrps) == 1
    assert 'FAKE1' in alldrps
    # FIXME: We should check that both are equal, not just the name
    assert alldrps['FAKE1'].name == ldrp.name


def test_drpsys_2_instruments(drpmocker):
    """Test that two DRPs are returned"""

    drpdata1 = pkgutil.get_data('numina.core.tests', 'drpfake1.yaml')
    drpdata2 = pkgutil.get_data('numina.core.tests', 'drpfake2.yaml')
    drpmocker.add_drp('FAKE1', drpdata1)
    drpmocker.add_drp('FAKE2', drpdata2)

    drpsys = DrpSystem()

    ldrp1 = drpsys.query_by_name('FAKE1')

    assert ldrp1 is not None
    assert ldrp1.name == 'FAKE1'

    ldrp2 = drpsys.query_by_name('FAKE2')

    assert ldrp2 is not None
    assert ldrp2.name == 'FAKE2'

    ldrp3 = drpsys.query_by_name('OTHER')
    assert ldrp3 is None

    alldrps = drpsys.query_all()
    assert len(alldrps) == 2
    assert 'FAKE1' in alldrps
    # FIXME: We should check that both are equal, not just the name
    assert alldrps['FAKE1'].name == ldrp1.name

    assert 'FAKE2' in alldrps
    # FIXME: We should check that both are equal, not just the name
    assert alldrps['FAKE2'].name == ldrp2.name


@pytest.mark.usefixtures("drpmocker")
def test_drpsys_no_instrument():

    drpsys = DrpSystem()

    ldrp1 = drpsys.query_by_name('FAKE1')

    assert ldrp1 is None

    ldrp2 = drpsys.query_by_name('FAKE2')

    assert ldrp2 is None

    ldrp3 = drpsys.query_by_name('OTHER')
    assert ldrp3 is None

    alldrps = drpsys.query_all()
    assert len(alldrps) == 0
