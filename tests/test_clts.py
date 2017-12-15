# coding: utf-8
from __future__ import unicode_literals, print_function, division
from util import test_data
import pytest
from clldutils.dsv import UnicodeReader


def test_translate(bipa, asjp):
    from pyclts import translate

    assert translate('ts a', bipa, asjp) == 'c E'
    assert translate('c a', asjp, bipa) == 'ts ɐ'


def test_getitem(bipa):
    s = bipa['a']
    assert bipa[s] == s
    assert bipa[s.name] == s


def test_ts_contains(bipa, asjp):
    assert bipa['ts'] in asjp


def test_ts_equality(bipa, asjp):
    asjp_ts = asjp[bipa['ts']]
    assert bipa['ts'] == asjp_ts


def test_examples(bipa):
    sound = bipa['dʷʱ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert not sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'
    assert sound.uname == 'LATIN SMALL LETTER D / MODIFIER LETTER SMALL W / MODIFIER LETTER SMALL H WITH HOOK'
    sound = bipa['dʱʷ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'


def test_parse(bipa):
    sounds = ['ʰdʱ', "ˈa", 'á']
    for s in sounds:
        res = bipa[s]
        assert res.generated
    for s in ['a', 't']:
        assert str(bipa[s]) == s
    
    # diphthongs
    dips = ['ao', 'ea', 'ai', 'ua']
    for s in dips:
        res = bipa[s]
        assert res.type == 'diphthong'
        assert res.name.endswith('diphthong')
        assert s == str(s)

    # clusters
    clus = ['tk', 'pk', 'dg', 'bdʰ']
    for s in clus:
        res = bipa[s]
        assert res.type == 'cluster'
        assert 'cluster' in res.name
        assert s == str(s)
        bipa._add(res)
        assert res in bipa

    # go for bad diacritics in front and end of a string
    assert bipa['*a'].type == 'unknownsound'
    assert bipa['a*'].type == 'unknownsound'


def test_call(bipa):
    assert bipa('th o x t a')[0].alias


def test_get(bipa):
    "test for the case that we have a new default"
    assert bipa.get('A', '?') == '?'


def test_sound_from_name(bipa):
    from pyclts.models import UnknownSound

    assert bipa['from unrounded open front to unrounded close-mid front diphthong'].grapheme == 'ae'
    assert bipa['from voiceless alveolar stop to voiceless velar stop cluster'].grapheme == 'tk'

    try:
        bipa['very bad feature voiced labial stop consonant']
    except ValueError:
        assert True
    try:
        bipa._from_name('very bad feature with bad consonantixs')
    except ValueError:
        assert True
    try:
        bipa._from_name('from something to something diphthong')
    except ValueError:
        assert True
    try:
        bipa._from_name('something diphthong')
    except ValueError:
        assert True

    assert bipa['pre-aspirated voiced bilabial nasal consonant'].generated
    assert not bipa._from_name('voiced nasal bilabial consonant').generated


def test_ts(bipa):
    from pyclts.transcriptionsystem import TranscriptionSystem
    from pyclts.models import Cluster,Diphthong
    try:
        TranscriptionSystem('')
    except ValueError:
        assert True
    try:
        TranscriptionSystem('_f1')
    except ValueError:
        assert True
    try:
        TranscriptionSystem('_f2')
    except ValueError:
        assert True
    try:
        bads = TranscriptionSystem('what')
    except ValueError:
        assert True


def test_models(bipa, asjp):
    from pyclts.models import Symbol
    sym = Symbol(ts=bipa, grapheme='s', source='s', generated=False, note='')
    assert str(sym) == sym.source == sym.grapheme
    assert sym == sym
    assert not sym.name
    assert sym.uname == "LATIN SMALL LETTER S"
    # complex sounds are always generated
    assert bipa['ae'].generated
    assert bipa['tk'].generated

    # equality tests in model for sound
    s1 = bipa['t']
    s2 = 't'
    assert s1 != s2

    # repr test for sound
    assert s1.name in repr(s1)

    # test the table function
    assert s1.table[1] == 'voiceless'
    assert '|' in bipa["ts'"].table[0]

    # test table for generated entities
    assert bipa['tk'].table[1] == bipa['t'].name

    # test the unicode name
    assert Symbol(ts='', grapheme=[['1', '2'], '2'], source='').uname == '-'

    # test complex sound
    assert str(bipa['ae']) == 'ae'

    # test equality of symbols
    assert Symbol(ts=bipa, grapheme='1', source='1') != Symbol(
            ts=asjp, grapheme='1', source='1')


def test_transcriptiondata(sca, dolgo, asjpd, phoible, pbase, bipa):

    seq = 'tʰ ɔ x ˈth ə r A ˈI ʲ'
    seq2 = 'th o ?/x a'
    seq3 = 'th o ?/ a'
    seq4 = 'ǃŋ i b ǃ'

    assert dolgo(seq) == list('TVKTVR000')
    assert sca(seq2)[2] == 'G'
    assert asjpd(seq2)[2] == 'x'
    assert sca(seq3)[2] == '0'

    # these tests need to be adjusted once lingpy accepts click sounds
    assert sca(seq4)[0] == '0'
    assert asjpd(seq4)[0] == '0'
    assert sca(seq4)[3] == '!'
    assert asjpd(seq4)[3] == '!'
    
    with pytest.raises(KeyError):
        dolgo['A']
        sca['B']

    # test data from sound name
    assert sca.resolve_sound(bipa['ʰb']) == 'P'
    assert sca.resolve_sound(bipa['ae']) == 'A'
    assert sca.resolve_sound(bipa['tk']) == 'T'


def test_transcription_system_consistency(bipa, asjp, gld):

    # bipa should always be able to be translated to
    for sound in asjp:
        #print(sound, asjp[sound].name)
        if sound not in bipa:
            assert '<?>' not in str(bipa[asjp[sound].name])
    for sound in gld:
        #print(sound, gld[sound].name)
        if sound not in bipa:
            assert '<?>' not in str(bipa[gld[sound].name])
    good = True
    for sound in bipa:
        if bipa[sound].type != 'unknownsound' and not bipa[sound].alias:
            if sound != str(bipa[sound]):
                print(sound, str(bipa[sound]))
                good = False
        elif bipa[sound].type == 'unknownsound':
            print(sound)
            good = False
    assert good == True
    good = True
    for sound in gld:
        if gld[sound].type != 'unknownsound' and not gld[sound].alias:
            if sound != str(gld[sound]):
                print(sound, str(gld[sound]))
                good = False
        elif gld[sound].type == 'unknownsound':
            print(sound)
            good = False
    assert good == True
    good = True
    for sound in asjp:
        if asjp[sound].type != 'unknownsound' and not asjp[sound].alias:
            if sound != str(asjp[sound]):
                print(sound, str(asjp[sound]))
                good = False
        elif asjp[sound].type == 'unknownsound':
            print(sound)
            good = False
    assert good == True

    # important test for alias
    assert str(bipa['d̤ʷ']) == str(bipa['dʷʱ']) == str(bipa['dʱʷ'])


def test_clicks(bipa):
    # test clicks data
    with UnicodeReader(test_data('clicks.tsv'), delimiter='\t') as f:
        for row in [r for r in f][1:]:
            grapheme = row[0]
            gtype = row[4]
            if gtype == 'stop-cluster':
                assert bipa[grapheme].type == 'cluster'


def test_datasets(bipa):
    """Test on a large pre-assembled dataset whether everything is consistent"""
    
    with UnicodeReader(test_data('test_data.tsv'), delimiter="\t") as f:
        rows = [r for r in f]
        for row in rows[1:]:
            tmp = dict(zip(rows[0], row))
            sound = bipa[tmp['source']]
            if sound.type not in ['unknownsound', 'marker']:
                if tmp['nfd-normalized'] == '+':
                    assert bipa[tmp['source']] != sound.source
                if tmp['clts-normalized'] == "+":
                    assert sound.normalized
                if tmp['aliased'] == '+':
                    assert sound.alias
                if tmp['generated']:
                    assert sound.generated
                if tmp['stressed']:
                    assert sound.stress
                assert sound.name == tmp['name']
                assert sound.codepoints == tmp['codepoints']
            