# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import fontforge
import magic
import os
import os.path
import re
import StringIO
import sys
import unicodedata


from contextlib import contextmanager
from fontTools import ttLib

from bakery_lint.base import BakeryTestCase as TestCase, tags, autofix, \
    TestCaseOperator
from bakery_cli.fixers import RenameFileWithSuggestedName
from bakery_cli.fixers import ReplaceOFLLicenseURL, ReplaceApacheLicenseURL, \
    ReplaceOFLLicenseWithShortLine, ReplaceApacheLicenseWithShortLine
from bakery_cli.fixers import NbspAndSpaceSameWidth, CharacterSymbolsFixer
from bakery_cli.fixers import get_unencoded_glyphs
from bakery_cli.ttfont import Font, FontTool, getSuggestedFontNameValues
from bakery_cli.utils import run
from bakery_cli.utils import UpstreamDirectory


REQUIRED_TABLES = set(['cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name',
                       'OS/2', 'post'])
OPTIONAL_TABLES = set(['cvt', 'fpgm', 'loca', 'prep',
                       'VORG', 'EBDT', 'EBLC', 'EBSC', 'BASE', 'GPOS',
                       'GSUB', 'JSTF', 'DSIG', 'gasp', 'hdmx', 'kern',
                       'LTSH', 'PCLT', 'VDMX', 'vhea', 'vmtx'])


@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


def getNameRecordValue(nameRecord):
    if nameRecord.isUnicode():
        return nameRecord.string.decode('utf-16-be')
    return nameRecord.string


class TTFTestCase(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @tags('info',)
    def test_version_in_name_table_is_in_correct_format(self):
        """ Version is in correct format in `name` table """
        ttfont = ttLib.TTFont(self.operator.path)

        def is_valid(value):
            return re.match(r'Version\s[1-9]+\.\d+', value)

        for name in ttfont['name'].names:
            value = getNameRecordValue(name)
            if name.nameID == 5 and not is_valid(value):
                self.fail(('The NAME id 5 string value must follow '
                           'the pattern Version X.Y. Current value: {}').format(value))


    def test_fontforge_openfile_contains_stderr(self):
        with redirect_stdout(StringIO.StringIO()) as std:
            fontforge.open(self.operator.path)
            if std.getvalue():
                self.fail('FontForge prints STDERR')

    @tags('info',)
    @autofix('bakery_cli.fixers.RenameFileWithSuggestedName')
    def test_source_ttf_font_filename_equals_familystyle(self):
        """ Source TTF Font filename equals family style """
        fixer = RenameFileWithSuggestedName(self, self.operator.path)
        self.assertEqual(fixer.validate(), os.path.basename(self.operator.path))

    def test_ttx_family_naming_recommendation(self):
        "The font follows the font family naming recommendation."
        # See http://forum.fontlab.com/index.php?topic=313.0
        font = Font.get_ttfont(self.operator.path)

        length = len(Font.bin2unistring(font['name'].getName(4, 3, 1, 1033)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(6, 3, 1, 1033)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        name = Font.bin2unistring(font['name'].getName(6, 3, 1, 1033))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(1, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(2, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(16, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(17, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        if 'OS/2' in font:
            # <Weight> value >= 250 and <= 900 in steps of 50
            self.assertTrue(bool(font['OS/2'].usWeightClass % 50 == 0),
                            msg=('OS/2 usWeightClass has to be in steps of 50.'
                                 ' Now: %s') % font['OS/2'].usWeightClass)

            self.assertGreaterEqual(font['OS/2'].usWeightClass, 250)
            self.assertLessEqual(font['OS/2'].usWeightClass, 900)

        if 'CFF' in font:
            self.assertTrue(bool(font['CFF'].Weight % 50 == 0),
                            msg=('CFF Weight has to be in steps of 50.'
                                 ' Now: %s') % font['CFF'].Weight)

            self.assertGreaterEqual(font['CFF'].Weight, 250)
            self.assertLessEqual(font['CFF'].Weight, 900)

    def test_glyphname_does_not_contain_disallowed_chars(self):
        """ GlyphName length < 30 and does contain allowed chars only """
        font = Font.get_ttfont(self.operator.path)

        for _, glyphName in enumerate(font.ttfont.getGlyphOrder()):
            if glyphName == '.notdef':
                continue
            if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
                self.fail(('Glyph "%s" does not comply conventions.'
                           ' A glyph name may be up to 31 characters in length,'
                           ' must be entirely comprised of characters from'
                           ' the following set:'
                           ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                           ' start with a digit or period. The only exception'
                           ' is the special character ".notdef". "twocents",'
                           ' "a1", and "_" are valid glyph names. "2cents"'
                           ' and ".twocents" are not.') % glyphName)

    def test_ttx_duplicate_glyphs(self):
        """ Font contains unique glyph names? """
        # (Duplicate glyph names prevent font installation on Mac OS X.)
        font = Font.get_ttfont(self.operator.path)
        glyphs = []
        for _, g in enumerate(font.ttfont.getGlyphOrder()):
            self.assertFalse(re.search(r'#\w+$', g),
                             msg="Font contains incorrectly named glyph %s" % g)
            glyphID = re.sub(r'#\w+', '', g)

            # Each GlyphID has to be unique in TTX
            self.assertFalse(glyphID in glyphs,
                             msg="GlyphID %s occurs twice in TTX" % g)
            glyphs.append(glyphs)

    def test_epar_in_keys(self):
        """ EPAR table present in font? """
        font = Font.get_ttfont(self.operator.path)
        self.assertIn('EPAR', font.ttfont.keys(), 'No')

    @tags('required')
    @autofix('bakery_cli.fixers.ResetFSTypeFlagFixer')
    def test_is_fstype_not_set(self):
        """ Is the OS/2 table fsType set to 0? """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.OS2_fsType, 0)

    def containsSubstr(self, nameRecord, substr):
        return substr in getNameRecordValue(nameRecord)

    @autofix('bakery_cli.fixers.RemoveItemsWithPlatformID1')
    def test_platformID_1_exists(self):
        """ Check if NAME table does not contain items with platformID = 1 """
        font = ttLib.TTFont(self.operator.path)
        items = [item for item in font['name'].names if item.platformID == 1]
        self.assertTrue(bool(items), "`name` table records should not contain platformID='1' records")

    @autofix('bakery_cli.fixers.RemoveNameRecordWithOpyright')
    def test_name_id_copyright(self):
        """ Is there `opyright` substring nameID in nameId (10) ? """
        font = ttLib.TTFont(self.operator.path)
        records = [f for f in font['name'].names
                   if self.containsSubstr(f, 'opyright') and f.nameID == 10]
        self.assertFalse(bool(records))

    @autofix('bakery_cli.fixers.ReplaceOFLLicenseWithShortLine')
    def test_name_id_of_license(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceOFLLicenseWithShortLine(self, self.operator.path)

        placeholder = fixer.get_placeholder()

        path = os.path.join(os.path.dirname(self.operator.path), 'OFL.txt')
        licenseexists = os.path.exists(path)

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                if value != placeholder and licenseexists:
                    self.fail('License file OFL.txt exists but NameID'
                              ' value is not specified for that.')

    @autofix('bakery_cli.fixers.GaspFixer', always_run=True)
    def test_check_gasp_table_type(self):
        """ Font table gasp should be 15 """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['gasp']
        except KeyError:
            self.fail('"GASP" table not found')

        if not isinstance(font['gasp'].gaspRange, dict):
            self.fail('GASP.gaspRange method value have wrong type')

        if 65535 not in font['gasp'].gaspRange:
            self.fail("GASP does not have 65535 gaspRange")

        # XXX: Needs review
        if font['gasp'].gaspRange[65535] != 15:
            self.fail('gaspRange[65535] value is not 15')

    def test_gpos_table_has_kerning_info(self):
        """ GPOS table has kerning information """
        font = Font.get_ttfont(self.operator.path)

        try:
            font['GPOS']
        except KeyError:
            self.fail('"GPOS" does not exist in font')
        flaglookup = False
        for lookup in font['GPOS'].table.LookupList.Lookup:
            if lookup.LookupType == 2:  # Adjust position of a pair of glyphs
                flaglookup = lookup
                break  # break for..loop to avoid reading all kerning info
        self.assertTrue(flaglookup, msg='GPOS doesnt have kerning information')
        self.assertGreater(flaglookup.SubTableCount, 0)
        self.assertGreater(flaglookup.SubTable[0].PairSetCount, 0)

    @autofix('bakery_cli.fixers.CharacterSymbolsFixer')
    def test_check_names_are_ascii_only(self):
        """ NAME and CFF tables must not contain non-ascii characters """
        font = Font.get_ttfont(self.operator.path)

        for name in font.names:
            string = Font.bin2unistring(name)
            marks = CharacterSymbolsFixer.unicode_marks(string)
            if marks:
                self.fail('Contains {}'.format(marks))

    def test_fontname_is_equal_to_macstyle(self):
        """ Check that fontname is equal to macstyle flags """
        font = Font.get_ttfont(self.operator.path)

        macStyle = font.macStyle

        try:
            fontname_style = font.fullname.split('-')[1]
        except IndexError:
            fontname_style = ''

        expected_style = ''
        if macStyle & 0b01:
            expected_style += 'Bold'

        if macStyle & 0b10:
            expected_style += 'Italic'

        if not bool(macStyle & 0b11):
            expected_style = 'Regular'

        if fontname_style != expected_style:
            _ = 'macStyle ({0}) supposed style ended with "{1}"'

            if fontname_style:
                _ += ' but ends with "{2}"'
            self.fail(_.format(bin(macStyle)[-2:], expected_style, fontname_style))

    @autofix('bakery_cli.fixers.ReplaceOFLLicenseURL')
    def test_name_id_of_license_url(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceOFLLicenseURL(self, self.operator.path)

        text = open(fixer.get_licensecontent_filename()).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path),
                                       'OFL.txt')

        isLicense = False

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:  # check license nameID only
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value

        self.assertFalse(isLicense and bool(fixer.validate()))

    @autofix('bakery_cli.fixers.ReplaceApacheLicenseWithShortLine')
    def test_name_id_apache_license(self):
        """ Is there Apache in nameId (13) ? """
        fixer = ReplaceApacheLicenseWithShortLine(self, self.operator.path)

        placeholder = fixer.get_placeholder()

        path = os.path.join(os.path.dirname(self.operator.path), 'LICENSE.txt')
        licenseexists = os.path.exists(path)

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                if value != placeholder and licenseexists:
                    self.fail('License file LICENSE.txt exists but NameID'
                              ' value is not specified for that.')

    @autofix('bakery_cli.fixers.ReplaceApacheLicenseURL')
    def test_name_id_apache_license_url(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceApacheLicenseURL(self, self.operator.path)

        text = open(fixer.get_licensecontent_filename()).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path),
                                       'LICENSE.txt')

        isLicense = False

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:  # check license nameID only
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value

        self.assertFalse(isLicense and bool(fixer.validate()))

    @tags('required',)
    def test_ots(self):
        """ Is TTF file correctly sanitized for Firefox and Chrome """
        stdout = run('{0} {1}'.format('ot-sanitise', self.operator.path),
                     os.path.dirname(self.operator.path),
                     log=self.operator.logger)
        self.assertEqual('', stdout.strip())

    @autofix('bakery_cli.fixers.CreateDSIGFixer')
    def test_check_font_has_dsig_table(self):
        """ Check that font has DSIG table """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['DSIG']
        except KeyError:
            self.fail('Font does not have "DSIG" table')

    def test_no_kern_table_exists(self):
        """ Check that no "KERN" table exists """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['KERN']
            self.fail('Font does have "KERN" table')
        except KeyError:
            pass

    def test_check_full_font_name_begins_with_family_name(self):
        """ Check if full font name begins with the font family name """
        font = Font.get_ttfont(self.operator.path)
        for entry in font.names:
            if entry.nameID != 1:
                continue
            for entry2 in font.names:
                if entry2.nameID != 4:
                    continue
                if (entry.platformID == entry2.platformID
                        and entry.platEncID == entry2.platEncID
                        and entry.langID == entry2.langID):

                    entry2value = Font.bin2unistring(entry2)
                    entryvalue = Font.bin2unistring(entry)
                    if not entry2value.startswith(entryvalue):
                        _ = ('Full font name does not begin with family'
                             ' name: FontFamilyName = "%s";'
                             ' FullFontName = "%s"')
                        self.fail(_ % (entryvalue, entry2value))

    def test_check_glyf_table_length(self):
        """ Check if there is unused data at the end of the glyf table """
        from fontTools import ttLib
        font = ttLib.TTFont(self.operator.path)
        # TODO: should this test support CFF as well?
        if 'CFF ' in font: self.skip("No 'glyf' table to check in a CFF font.")

        expected = font.reader.tables['loca'].length
        actual = font.reader.tables['glyf'].length
        diff = actual - expected

        # allow up to 3 bytes of padding
        if diff > 3:
            _ = ("Glyf table has unreachable data at the end of the table."
                 " Expected glyf table length %s (from loca table), got length"
                 " %s (difference: %s)") % (expected, actual, diff)
            self.fail(_)
        elif diff < 0:
            _ = ("Loca table references data beyond the end of the glyf table."
                 " Expected glyf table length %s (from loca table), got length"
                 " %s (difference: %s)") % (expected, actual, diff)
            self.fail(_)

    def assertExists(self, d):
        font = Font.get_ttfont(self.operator.path)
        glyphs = font.retrieve_cmap_format_4().cmap
        if not bool(ord(unicodedata.lookup(d)) in glyphs):
            self.fail('%s does not exist in font' % d)

    @tags('required')
    def test_nbsp(self):
        """ Check if 'NO-BREAK SPACE' exists"""
        self.assertExists('NO-BREAK SPACE')

    @tags('required',)
    def test_space(self):
        """ Check if 'SPACE' exists """
        self.assertExists('SPACE')

    def test_euro(self):
        """ Check if 'EURO SIGN' exists """
        self.assertExists('EURO SIGN')

    def test_check_hmtx_hhea_max_advance_width_agreement(self):
        """ Check if MaxAdvanceWidth agree in the Hmtx and Hhea tables """
        font = Font.get_ttfont(self.operator.path)

        hmtx_advance_width_max = font.get_hmtx_max_advanced_width()
        hhea_advance_width_max = font.advance_width_max
        error = ("AdvanceWidthMax mismatch: expected %s (from hmtx);"
                 " got %s (from hhea)") % (hmtx_advance_width_max,
                                           hhea_advance_width_max)
        self.assertEqual(hmtx_advance_width_max,
                         hhea_advance_width_max, error)

    @tags('required')
    def test_check_italic_angle_agreement(self):
        """ Check italicangle property zero or negative """
        font = Font.get_ttfont(self.operator.path)
        if font.italicAngle > 0:
            self.fail('italicAngle must be less or equal zero')
        if abs(font.italicAngle) > 20:
            self.fail('italicAngle can\'t be larger than 20 degrees')

    def test_prep_magic_code(self):
        """ Font contains in PREP table magic code """
        magiccode = '\xb8\x01\xff\x85\xb0\x04\x8d'
        font = Font.get_ttfont(self.operator.path)
        if 'CFF ' in font: self.skip("Not applicable to a CFF font.")
        try:
            bytecode = font.get_program_bytecode()
        except KeyError:
            bytecode = ''
        self.assertTrue(bytecode == magiccode,
                        msg='PREP does not contain magic code')

    @autofix('bakery_cli.fixers.FamilyAndStyleNameFixer')
    def test_check_stylename_is_under_recommendations(self):
        """ Style name must be equal to one of the following four
            values: "Regular", "Italic", "Bold" or "Bold Italic" """
        font = Font.get_ttfont(self.operator.path)
        self.assertIn(str(font.ot_style_name), ['Regular', 'Italic',
                                                'Bold', 'Bold Italic'])

    @autofix('bakery_cli.fixers.FamilyAndStyleNameFixer')
    def test_check_opentype_familyname(self):
        """ OT Family Name for Windows should be equal to Family Name """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_family_name, font.familyname)

    @autofix('bakery_cli.fixers.FamilyAndStyleNameFixer')
    def test_check_opentype_fullname(self):
        """ Full name matches Windows-only Opentype-specific FullName """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_full_name, font.fullname)

    @autofix('bakery_cli.fixers.FamilyAndStyleNameFixer')
    def test_suggested_subfamily_name(self):
        """ Family does not contain subfamily in `name` table """
        # Currently we just look that family does not contain any spaces
        # in its name. This prevent us from incorrect suggestions of names
        font = Font.get_ttfont(self.operator.path)
        suggestedvalues = getSuggestedFontNameValues(font.ttfont)
        self.assertEqual(font.familyname, suggestedvalues['family'])
        self.assertEqual(font.stylename, suggestedvalues['subfamily'])

    @tags('required')
    def test_check_names_same_across_platforms(self):
        """ Font names are same across specific-platforms """
        font = Font.get_ttfont(self.operator.path)

        for name in font.names:
            for name2 in font.names:
                if name.nameID != name2.nameID:
                    continue

                if self.diff_platform(name, name2) \
                        or self.diff_platform(name2, name):
                    _name = Font.bin2unistring(name)
                    _name2 = Font.bin2unistring(name2)
                    if _name != _name2:
                        msg = ('Names in "name" table are not the same'
                               ' across specific-platforms')
                        self.fail(msg)

    def diff_platform(self, name, name2):
        return (name.platformID == 3 and name.langID == 0x409
                and name2.platformID == 1 and name2.langID == 0)

    @tags('required')
    @autofix('bakery_cli.fixers.NbspAndSpaceSameWidth')
    def test_check_nbsp_width_matches_sp_width(self):
        """ Check non-breaking space's advancewidth is the same as space """
        checker = NbspAndSpaceSameWidth(self, self.operator.path)

        space = checker.getGlyph(0x0020)
        nbsp = checker.getGlyph(0x00A0)
        tab = checker.getGlyph(0x0009)

        self.assertTrue(space, "Font does not contain a space glyph")
        self.assertTrue(nbsp, "Font does not contain a nbsp glyph")
        self.assertTrue(tab, "Font does not contain a tab glyph")

        spaceWidth = checker.getWidth(space)
        nbspWidth = checker.getWidth(nbsp)
        tabWidth = checker.getWidth(tab)
        self.assertEqual(spaceWidth, nbspWidth,
                         ("The nbsp advance width does not match "
                          "the space advance width"))
        self.assertEqual(spaceWidth, tabWidth,
                         ("The tab advance width does not match "
                          "the space advance width"))

    def test_check_no_problematic_formats(self):
        """ Check that font contain required tables """
        font = ttLib.TTFont(self.operator.path)
        tables = set(font.reader.tables.keys())
        desc = []
        glyphs = set(['glyf'] if 'glyf' in font else ['CFF '])
        if REQUIRED_TABLES + glyphs - tables:
            desc += ["Font is missing required tables: [%s]" % ', '.join(str(t) for t in (REQUIRED_TABLES + glyphs - tables))]
            if OPTIONAL_TABLES & tables:
                desc += ["includes optional tables %s" % ', '.join(str(t) for t in (OPTIONAL_TABLES & tables))]
        if desc:
            self.fail(' but '.join(desc))

    def test_check_os2_width_class(self):
        font = Font.get_ttfont(self.operator.path)
        error = "OS/2 widthClass must be [1..9] inclusive, was %s IE9 fail"
        error = error % font.OS2_usWidthClass
        self.assertIn(font.OS2_usWidthClass, range(1, 10), error)

    def test_check_panose_identification(self):
        """ Check if Panose is not set to monospaced if advancewidth of
            all glyphs is not equal to each others """
        font = Font.get_ttfont(self.operator.path)

        if font['OS/2'].panose.bProportion == 9:
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    link = ('http://www.thomasphinney.com/2013/01'
                            '/obscure-panose-issues-for-font-makers/')
                    self.fail(('Your font does not seem monospaced but PANOSE'
                               ' bProportion set to monospace. It may have '
                               ' a bug in windows. Details: %s' % link))
                prev = font.advance_width(g)

    @tags('note')
    @autofix('bakery_cli.fixers.AddSPUAByGlyphIDToCmap')
    def test_font_unencoded_glyphs(self):
        """ Font does not have unencoded glyphs """
        ttx = ttLib.TTFont(self.operator.path, 0)
        unencoded_glyphs = get_unencoded_glyphs(ttx)
        self.assertIs(unencoded_glyphs, [],
                      msg='There should not be unencoded glyphs')

    def test_check_upm_heigths_less_120(self):
        """ Check if UPM Heights NOT more than 120% """
        ttfont = Font.get_ttfont(self.operator.path)
        value = ttfont.ascents.get_max() + abs(ttfont.descents.get_min())
        value = value * 100 / float(ttfont.get_upm_height())
        if value > 120:
            _ = "UPM:Height is %d%%, consider redesigning to 120%% or less"
            self.fail(_ % value)

    @autofix('bakery_cli.fixers.Vmet')
    def test_metrics_linegaps_are_zero(self):
        """ Check that linegaps in tables are zero """
        dirname = os.path.dirname(self.operator.path)

        directory = UpstreamDirectory(dirname)

        fonts_gaps_are_not_zero = []
        for filename in directory.BIN:
            ttfont = Font.get_ttfont(os.path.join(dirname, filename))
            if bool(ttfont.linegaps.os2typo) or bool(ttfont.linegaps.hhea):
                fonts_gaps_are_not_zero.append(filename)

        if fonts_gaps_are_not_zero:
            _ = '[%s] have not zero linegaps'
            self.fail(_ % ', '.join(fonts_gaps_are_not_zero))

    @autofix('bakery_cli.fixers.Vmet')
    def test_metrics_ascents_equal_bbox(self):
        """ Check that ascents values are same as max glyph point """
        dirname = os.path.dirname(self.operator.path)

        ymax, fonts_ascents_not_bbox = self.get_fonts(dirname)

        if fonts_ascents_not_bbox:
            _ = '[%s] ascents differ to maximum value: %s'
            self.fail(_ % (', '.join(fonts_ascents_not_bbox), ymax))

    def get_fonts(self, dirname):
        directory = UpstreamDirectory(dirname)

        fonts_ascents_not_bbox = []
        ymax = 0

        _cache = {}
        for filename in directory.get_binaries():
            ttfont = Font.get_ttfont(os.path.join(dirname, filename))

            _, ymax_ = ttfont.get_bounding()
            ymax = max(ymax, ymax_)

            _cache[filename] = {
                'os2typo': ttfont.ascents.os2typo,
                'os2win': ttfont.ascents.os2win,
                'hhea': ttfont.ascents.hhea
            }

        for filename, data in _cache.items():
            if [data['os2typo'], data['os2win'], data['hhea']] != [ymax] * 3:
                fonts_ascents_not_bbox.append(filename)
        return ymax, fonts_ascents_not_bbox

    @autofix('bakery_cli.fixers.Vmet')
    def test_metrics_descents_equal_bbox(self):
        """ Check that descents values are same as min glyph point """
        dirname = os.path.dirname(self.operator.path)

        directory = UpstreamDirectory(dirname)

        fonts_descents_not_bbox = []
        ymin = 0

        _cache = {}
        for filename in directory.get_binaries():
            ttfont = Font.get_ttfont(os.path.join(dirname, filename))

            ymin_, _ = ttfont.get_bounding()
            ymin = min(ymin, ymin_)

            _cache[filename] = {
                'os2typo': abs(ttfont.descents.os2typo),
                'os2win': abs(ttfont.descents.os2win),
                'hhea': abs(ttfont.descents.hhea)
            }

        for filename, data in _cache.items():
            datas = [data['os2typo'], data['os2win'], data['hhea']]
            if datas != [abs(ymin)] * 3:
                fonts_descents_not_bbox.append(filename)

        if fonts_descents_not_bbox:
            _ = '[%s] ascents differ to minimum value: %s'
            self.fail(_ % (', '.join(fonts_descents_not_bbox), ymin))

    @tags('required')
    def test_license_included_in_font_names(self):
        """ Check font has a correct license url """
        font = Font.get_ttfont(self.operator.path)

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not regex.match(font.license_url):
            self.fail("LicenseUrl is required and must be correct url")


class FontForgeValidateStateTest(TestCase):

    targets = ['result']
    tool = 'FontForge'
    name = __name__

    def setUp(self):
        font = fontforge.open(self.operator.path)
        self.validation_state = font.validate()

    def test_validation_open_contours(self):
        """ Contours are closed """
        self.assertFalse(bool(self.validation_state & 0x2))

    def test_validation_glyph_intersect(self):
        """ Contours do not intersect """
        self.assertFalse(bool(self.validation_state & 0x4))

    def test_wrong_direction_in_glyphs(self):
        """ Contours have correct directions """
        self.assertFalse(bool(self.validation_state & 0x8))

    def test_flipped_reference_in_glyphs(self):
        """ References in the glyph haven't been flipped """
        self.assertFalse(bool(self.validation_state & 0x10))

    def test_missing_extrema_in_glyphs(self):
        """ Glyphs have points at extremas """
        self.assertFalse(bool(self.validation_state & 0x20))

    def test_referenced_glyphs_are_present(self):
        """ Glyph names referred to from glyphs present in the font """
        self.assertFalse(bool(self.validation_state & 0x40))

    def test_points_are_not_too_far_apart(self):
        """ Points (or control points) are not too far apart """
        self.assertFalse(bool(self.validation_state & 0x40000))

    def test_postscript_hasnt_limit_points_in_glyphs(self):
        """ Not more than 1,500 points in any glyph (a PostScript limit) """
        self.assertFalse(bool(self.validation_state & 0x80))

    def test_postscript_hasnt_limit_hints_in_glyphs(self):
        """ PostScript hasnt a limit of 96 hints in glyphs """
        self.assertFalse(bool(self.validation_state & 0x100))

    def test_valid_glyph_names(self):
        """ Font doesn't have invalid glyph names """
        self.assertFalse(bool(self.validation_state & 0x200))

    def test_allowed_numbers_points_in_glyphs(self):
        """ Glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x400))

    def test_allowed_numbers_paths_in_glyphs(self):
        """ Glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x800))

    def test_allowed_numbers_points_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x1000))

    def test_allowed_numbers_paths_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x2000))

    def test_valid_length_instructions(self):
        """ Glyphs instructions have valid lengths """
        self.assertFalse(bool(self.validation_state & 0x4000))

    def test_points_are_integer_aligned(self):
        """ Points in glyphs are integer aligned """
        self.assertFalse(bool(self.validation_state & 0x80000))

    def test_missing_anchors(self):
        """ Glyphs have all required anchors.
            (According to the opentype spec, if a glyph contains an anchor point
            for one anchor class in a subtable, it must contain anchor points
            for all anchor classes in the subtable. Even it, logically,
            they do not apply and are unnecessary.) """
        self.assertFalse(bool(self.validation_state & 0x100000))

    def test_duplicate_glyphs(self):
        """ Glyph names are unique. """
        self.assertFalse(bool(self.validation_state & 0x200000))

    def test_duplicate_unicode_codepoints(self):
        """ Unicode code points are unique. """
        self.assertFalse(bool(self.validation_state & 0x400000))

    def test_overlapped_hints(self):
        """ Hints do not overlap """
        self.assertFalse(bool(self.validation_state & 0x800000))


class CheckFontAgreements(TestCase):

    name = __name__
    targets = ['result']
    tool = 'lint'

    def setUp(self):
        self.font = Font.get_ttfont(self.operator.path)

    @tags('note')
    def test_em_is_1000(self):
        """ Font em size should be 1000, but doesn't have to be """
        self.assertEqual(self.font.get_upm_height(), 1000)

    @tags('required')
    def test_font_is_font(self):
        """ File provided as parameter is TTF font file """
        self.assertTrue(magic.from_file(self.operator.path, mime=True),
                        'application/x-font-ttf')

    @tags('required')
    def test_latin_file_exists(self):
        """ GF requires a latin subset, so we check that font file exists """
        path = os.path.dirname(self.operator.path)
        path = os.path.join(path, self.operator.path[:-3] + "latin")
        self.assertTrue(os.path.exists(path))

    @tags('required')
    def test_menu_file_exists(self):
        """ GF requires a menu subset, so we check that font file exists """
        path = os.path.dirname(self.operator.path)
        path = os.path.join(path, self.operator.path[:-3] + "menu")
        self.assertTrue(os.path.exists(path))


class TestKerningPairs(TestCase):

    targets = 'result'
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        ttf = ttLib.TTFont(cls.operator.path)
        return 'kern' not in ttf

    @tags("info")
    def test_kerning_pairs(self):
        """ Number of kerning pairs? """
        ttf = ttLib.TTFont(self.operator.path)
        glyphs = len(ttf['glyf'].glyphs)
        kerningpairs = len(ttf['kern'].kernTables[0].kernTable.keys())
        msg = "Kerning pairs to total glyphs is {0}:{1}"
        self.fail(msg.format(glyphs, kerningpairs))


def get_suite(path, apply_autofix=False):
    import unittest
    suite = unittest.TestSuite()

    testcases = [
        TTFTestCase,
        FontForgeValidateStateTest,
        CheckFontAgreements,
        TestKerningPairs
    ]

    for testcase in testcases:

        testcase.operator = TestCaseOperator(path)
        testcase.apply_fix = apply_autofix

        if getattr(testcase, 'skipUnless', False):
            if testcase.skipUnless():
                continue

        if getattr(testcase, '__generateTests__', None):
            testcase.__generateTests__()
        
        for test in unittest.defaultTestLoader.loadTestsFromTestCase(testcase):
            suite.addTest(test)

    return suite