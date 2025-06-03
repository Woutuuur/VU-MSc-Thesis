/*
 * Copyright (c) 2023, Oracle and/or its affiliates. All rights reserved.
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.  Oracle designates this
 * particular file as subject to the "Classpath" exception as provided
 * by Oracle in the LICENSE file that accompanied this code.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * Please contact Oracle, 500 Oracle Parkway, Redwood Shores, CA 94065 USA
 * or visit www.oracle.com if you need additional information or have any
 * questions.
 */

package jdk.internal.util.regex;

/**
 * Helper class for supporting the GB9c rule in Unicode Text Segmentation TR29
 *
 * <blockquote>
 * GB9c Do not break within certain combinations with Indic_Conjunct_Break (InCB)=Linker.
 *
 * \p{InCB=Consonant} [ \p{InCB=Extend} \p{InCB=Linker} ]* \p{InCB=Linker} [ \p{InCB=Extend} \p{InCB=Linker} ]* x \p{InCB=Consonant}*
 * </blockquote>
 *
 * Code point conditions included in this class are derived from the "Derived Property: Indic_Conjunct_Break"
 * section in DerivedCoreProperties.txt of the Unicode Character Database.
 */
final class IndicConjunctBreak {
    static boolean isLinker(int cp) {
        return
            cp == 0x094D ||
            cp == 0x09CD ||
            cp == 0x0ACD ||
            cp == 0x0B4D ||
            cp == 0x0C4D ||
            cp == 0x0D4D;
    }

    static boolean isExtend(int cp) {
        return
           (cp >= 0x0300 && cp <= 0x036F) ||
           (cp >= 0x0483 && cp <= 0x0489) ||
           (cp >= 0x0591 && cp <= 0x05BD) ||
            cp == 0x05BF ||
            cp == 0x05C1 ||
            cp == 0x05C2 ||
            cp == 0x05C4 ||
            cp == 0x05C5 ||
            cp == 0x05C7 ||
           (cp >= 0x0610 && cp <= 0x061A) ||
           (cp >= 0x064B && cp <= 0x065F) ||
            cp == 0x0670 ||
           (cp >= 0x06D6 && cp <= 0x06DC) ||
           (cp >= 0x06DF && cp <= 0x06E4) ||
            cp == 0x06E7 ||
            cp == 0x06E8 ||
           (cp >= 0x06EA && cp <= 0x06ED) ||
            cp == 0x0711 ||
           (cp >= 0x0730 && cp <= 0x074A) ||
           (cp >= 0x07A6 && cp <= 0x07B0) ||
           (cp >= 0x07EB && cp <= 0x07F3) ||
            cp == 0x07FD ||
           (cp >= 0x0816 && cp <= 0x0819) ||
           (cp >= 0x081B && cp <= 0x0823) ||
           (cp >= 0x0825 && cp <= 0x0827) ||
           (cp >= 0x0829 && cp <= 0x082D) ||
           (cp >= 0x0859 && cp <= 0x085B) ||
           (cp >= 0x0897 && cp <= 0x089F) ||
           (cp >= 0x08CA && cp <= 0x08E1) ||
           (cp >= 0x08E3 && cp <= 0x0902) ||
            cp == 0x093A ||
            cp == 0x093C ||
           (cp >= 0x0941 && cp <= 0x0948) ||
           (cp >= 0x0951 && cp <= 0x0957) ||
            cp == 0x0962 ||
            cp == 0x0963 ||
            cp == 0x0981 ||
            cp == 0x09BC ||
            cp == 0x09BE ||
           (cp >= 0x09C1 && cp <= 0x09C4) ||
            cp == 0x09D7 ||
            cp == 0x09E2 ||
            cp == 0x09E3 ||
            cp == 0x09FE ||
            cp == 0x0A01 ||
            cp == 0x0A02 ||
            cp == 0x0A3C ||
            cp == 0x0A41 ||
            cp == 0x0A42 ||
            cp == 0x0A47 ||
            cp == 0x0A48 ||
           (cp >= 0x0A4B && cp <= 0x0A4D) ||
            cp == 0x0A51 ||
            cp == 0x0A70 ||
            cp == 0x0A71 ||
            cp == 0x0A75 ||
            cp == 0x0A81 ||
            cp == 0x0A82 ||
            cp == 0x0ABC ||
           (cp >= 0x0AC1 && cp <= 0x0AC5) ||
            cp == 0x0AC7 ||
            cp == 0x0AC8 ||
            cp == 0x0AE2 ||
            cp == 0x0AE3 ||
           (cp >= 0x0AFA && cp <= 0x0AFF) ||
            cp == 0x0B01 ||
            cp == 0x0B3C ||
            cp == 0x0B3E ||
            cp == 0x0B3F ||
           (cp >= 0x0B41 && cp <= 0x0B44) ||
           (cp >= 0x0B55 && cp <= 0x0B57) ||
            cp == 0x0B62 ||
            cp == 0x0B63 ||
            cp == 0x0B82 ||
            cp == 0x0BBE ||
            cp == 0x0BC0 ||
            cp == 0x0BCD ||
            cp == 0x0BD7 ||
            cp == 0x0C00 ||
            cp == 0x0C04 ||
            cp == 0x0C3C ||
           (cp >= 0x0C3E && cp <= 0x0C40) ||
           (cp >= 0x0C46 && cp <= 0x0C48) ||
           (cp >= 0x0C4A && cp <= 0x0C4C) ||
            cp == 0x0C55 ||
            cp == 0x0C56 ||
            cp == 0x0C62 ||
            cp == 0x0C63 ||
            cp == 0x0C81 ||
            cp == 0x0CBC ||
            cp == 0x0CBF ||
            cp == 0x0CC0 ||
            cp == 0x0CC2 ||
           (cp >= 0x0CC6 && cp <= 0x0CC8) ||
           (cp >= 0x0CCA && cp <= 0x0CCD) ||
            cp == 0x0CD5 ||
            cp == 0x0CD6 ||
            cp == 0x0CE2 ||
            cp == 0x0CE3 ||
            cp == 0x0D00 ||
            cp == 0x0D01 ||
            cp == 0x0D3B ||
            cp == 0x0D3C ||
            cp == 0x0D3E ||
           (cp >= 0x0D41 && cp <= 0x0D44) ||
            cp == 0x0D57 ||
            cp == 0x0D62 ||
            cp == 0x0D63 ||
            cp == 0x0D81 ||
            cp == 0x0DCA ||
            cp == 0x0DCF ||
           (cp >= 0x0DD2 && cp <= 0x0DD4) ||
            cp == 0x0DD6 ||
            cp == 0x0DDF ||
            cp == 0x0E31 ||
           (cp >= 0x0E34 && cp <= 0x0E3A) ||
           (cp >= 0x0E47 && cp <= 0x0E4E) ||
            cp == 0x0EB1 ||
           (cp >= 0x0EB4 && cp <= 0x0EBC) ||
           (cp >= 0x0EC8 && cp <= 0x0ECE) ||
            cp == 0x0F18 ||
            cp == 0x0F19 ||
            cp == 0x0F35 ||
            cp == 0x0F37 ||
            cp == 0x0F39 ||
           (cp >= 0x0F71 && cp <= 0x0F7E) ||
           (cp >= 0x0F80 && cp <= 0x0F84) ||
            cp == 0x0F86 ||
            cp == 0x0F87 ||
           (cp >= 0x0F8D && cp <= 0x0F97) ||
           (cp >= 0x0F99 && cp <= 0x0FBC) ||
            cp == 0x0FC6 ||
           (cp >= 0x102D && cp <= 0x1030) ||
           (cp >= 0x1032 && cp <= 0x1037) ||
            cp == 0x1039 ||
            cp == 0x103A ||
            cp == 0x103D ||
            cp == 0x103E ||
            cp == 0x1058 ||
            cp == 0x1059 ||
           (cp >= 0x105E && cp <= 0x1060) ||
           (cp >= 0x1071 && cp <= 0x1074) ||
            cp == 0x1082 ||
            cp == 0x1085 ||
            cp == 0x1086 ||
            cp == 0x108D ||
            cp == 0x109D ||
           (cp >= 0x135D && cp <= 0x135F) ||
           (cp >= 0x1712 && cp <= 0x1715) ||
           (cp >= 0x1732 && cp <= 0x1734) ||
            cp == 0x1752 ||
            cp == 0x1753 ||
            cp == 0x1772 ||
            cp == 0x1773 ||
            cp == 0x17B4 ||
            cp == 0x17B5 ||
           (cp >= 0x17B7 && cp <= 0x17BD) ||
            cp == 0x17C6 ||
           (cp >= 0x17C9 && cp <= 0x17D3) ||
            cp == 0x17DD ||
           (cp >= 0x180B && cp <= 0x180D) ||
            cp == 0x180F ||
            cp == 0x1885 ||
            cp == 0x1886 ||
            cp == 0x18A9 ||
           (cp >= 0x1920 && cp <= 0x1922) ||
            cp == 0x1927 ||
            cp == 0x1928 ||
            cp == 0x1932 ||
           (cp >= 0x1939 && cp <= 0x193B) ||
            cp == 0x1A17 ||
            cp == 0x1A18 ||
            cp == 0x1A1B ||
            cp == 0x1A56 ||
           (cp >= 0x1A58 && cp <= 0x1A5E) ||
            cp == 0x1A60 ||
            cp == 0x1A62 ||
           (cp >= 0x1A65 && cp <= 0x1A6C) ||
           (cp >= 0x1A73 && cp <= 0x1A7C) ||
            cp == 0x1A7F ||
           (cp >= 0x1AB0 && cp <= 0x1ACE) ||
           (cp >= 0x1B00 && cp <= 0x1B03) ||
           (cp >= 0x1B34 && cp <= 0x1B3D) ||
           (cp >= 0x1B42 && cp <= 0x1B44) ||
           (cp >= 0x1B6B && cp <= 0x1B73) ||
            cp == 0x1B80 ||
            cp == 0x1B81 ||
           (cp >= 0x1BA2 && cp <= 0x1BA5) ||
           (cp >= 0x1BA8 && cp <= 0x1BAD) ||
            cp == 0x1BE6 ||
            cp == 0x1BE8 ||
            cp == 0x1BE9 ||
            cp == 0x1BED ||
           (cp >= 0x1BEF && cp <= 0x1BF3) ||
           (cp >= 0x1C2C && cp <= 0x1C33) ||
            cp == 0x1C36 ||
            cp == 0x1C37 ||
           (cp >= 0x1CD0 && cp <= 0x1CD2) ||
           (cp >= 0x1CD4 && cp <= 0x1CE0) ||
           (cp >= 0x1CE2 && cp <= 0x1CE8) ||
            cp == 0x1CED ||
            cp == 0x1CF4 ||
            cp == 0x1CF8 ||
            cp == 0x1CF9 ||
           (cp >= 0x1DC0 && cp <= 0x1DFF) ||
            cp == 0x200D ||
           (cp >= 0x20D0 && cp <= 0x20F0) ||
           (cp >= 0x2CEF && cp <= 0x2CF1) ||
            cp == 0x2D7F ||
           (cp >= 0x2DE0 && cp <= 0x2DFF) ||
           (cp >= 0x302A && cp <= 0x302F) ||
            cp == 0x3099 ||
            cp == 0x309A ||
           (cp >= 0xA66F && cp <= 0xA672) ||
           (cp >= 0xA674 && cp <= 0xA67D) ||
            cp == 0xA69E ||
            cp == 0xA69F ||
            cp == 0xA6F0 ||
            cp == 0xA6F1 ||
            cp == 0xA802 ||
            cp == 0xA806 ||
            cp == 0xA80B ||
            cp == 0xA825 ||
            cp == 0xA826 ||
            cp == 0xA82C ||
            cp == 0xA8C4 ||
            cp == 0xA8C5 ||
           (cp >= 0xA8E0 && cp <= 0xA8F1) ||
            cp == 0xA8FF ||
           (cp >= 0xA926 && cp <= 0xA92D) ||
           (cp >= 0xA947 && cp <= 0xA951) ||
            cp == 0xA953 ||
           (cp >= 0xA980 && cp <= 0xA982) ||
            cp == 0xA9B3 ||
           (cp >= 0xA9B6 && cp <= 0xA9B9) ||
            cp == 0xA9BC ||
            cp == 0xA9BD ||
            cp == 0xA9C0 ||
            cp == 0xA9E5 ||
           (cp >= 0xAA29 && cp <= 0xAA2E) ||
            cp == 0xAA31 ||
            cp == 0xAA32 ||
            cp == 0xAA35 ||
            cp == 0xAA36 ||
            cp == 0xAA43 ||
            cp == 0xAA4C ||
            cp == 0xAA7C ||
            cp == 0xAAB0 ||
           (cp >= 0xAAB2 && cp <= 0xAAB4) ||
            cp == 0xAAB7 ||
            cp == 0xAAB8 ||
            cp == 0xAABE ||
            cp == 0xAABF ||
            cp == 0xAAC1 ||
            cp == 0xAAEC ||
            cp == 0xAAED ||
            cp == 0xAAF6 ||
            cp == 0xABE5 ||
            cp == 0xABE8 ||
            cp == 0xABED ||
            cp == 0xFB1E ||
           (cp >= 0xFE00 && cp <= 0xFE0F) ||
           (cp >= 0xFE20 && cp <= 0xFE2F) ||
            cp == 0xFF9E ||
            cp == 0xFF9F ||
            cp == 0x101FD ||
            cp == 0x102E0 ||
           (cp >= 0x10376 && cp <= 0x1037A) ||
           (cp >= 0x10A01 && cp <= 0x10A03) ||
            cp == 0x10A05 ||
            cp == 0x10A06 ||
           (cp >= 0x10A0C && cp <= 0x10A0F) ||
           (cp >= 0x10A38 && cp <= 0x10A3A) ||
            cp == 0x10A3F ||
            cp == 0x10AE5 ||
            cp == 0x10AE6 ||
           (cp >= 0x10D24 && cp <= 0x10D27) ||
           (cp >= 0x10D69 && cp <= 0x10D6D) ||
            cp == 0x10EAB ||
            cp == 0x10EAC ||
           (cp >= 0x10EFC && cp <= 0x10EFF) ||
           (cp >= 0x10F46 && cp <= 0x10F50) ||
           (cp >= 0x10F82 && cp <= 0x10F85) ||
            cp == 0x11001 ||
           (cp >= 0x11038 && cp <= 0x11046) ||
            cp == 0x11070 ||
            cp == 0x11073 ||
            cp == 0x11074 ||
           (cp >= 0x1107F && cp <= 0x11081) ||
           (cp >= 0x110B3 && cp <= 0x110B6) ||
            cp == 0x110B9 ||
            cp == 0x110BA ||
            cp == 0x110C2 ||
           (cp >= 0x11100 && cp <= 0x11102) ||
           (cp >= 0x11127 && cp <= 0x1112B) ||
           (cp >= 0x1112D && cp <= 0x11134) ||
            cp == 0x11173 ||
            cp == 0x11180 ||
            cp == 0x11181 ||
           (cp >= 0x111B6 && cp <= 0x111BE) ||
            cp == 0x111C0 ||
           (cp >= 0x111C9 && cp <= 0x111CC) ||
            cp == 0x111CF ||
           (cp >= 0x1122F && cp <= 0x11231) ||
           (cp >= 0x11234 && cp <= 0x11237) ||
            cp == 0x1123E ||
            cp == 0x11241 ||
            cp == 0x112DF ||
           (cp >= 0x112E3 && cp <= 0x112EA) ||
            cp == 0x11300 ||
            cp == 0x11301 ||
            cp == 0x1133B ||
            cp == 0x1133C ||
            cp == 0x1133E ||
            cp == 0x11340 ||
            cp == 0x1134D ||
            cp == 0x11357 ||
           (cp >= 0x11366 && cp <= 0x1136C) ||
           (cp >= 0x11370 && cp <= 0x11374) ||
            cp == 0x113B8 ||
           (cp >= 0x113BB && cp <= 0x113C0) ||
            cp == 0x113C2 ||
            cp == 0x113C5 ||
           (cp >= 0x113C7 && cp <= 0x113C9) ||
           (cp >= 0x113CE && cp <= 0x113D0) ||
            cp == 0x113D2 ||
            cp == 0x113E1 ||
            cp == 0x113E2 ||
           (cp >= 0x11438 && cp <= 0x1143F) ||
           (cp >= 0x11442 && cp <= 0x11444) ||
            cp == 0x11446 ||
            cp == 0x1145E ||
            cp == 0x114B0 ||
           (cp >= 0x114B3 && cp <= 0x114B8) ||
            cp == 0x114BA ||
            cp == 0x114BD ||
            cp == 0x114BF ||
            cp == 0x114C0 ||
            cp == 0x114C2 ||
            cp == 0x114C3 ||
            cp == 0x115AF ||
           (cp >= 0x115B2 && cp <= 0x115B5) ||
            cp == 0x115BC ||
            cp == 0x115BD ||
            cp == 0x115BF ||
            cp == 0x115C0 ||
            cp == 0x115DC ||
            cp == 0x115DD ||
           (cp >= 0x11633 && cp <= 0x1163A) ||
            cp == 0x1163D ||
            cp == 0x1163F ||
            cp == 0x11640 ||
            cp == 0x116AB ||
            cp == 0x116AD ||
           (cp >= 0x116B0 && cp <= 0x116B7) ||
            cp == 0x1171D ||
            cp == 0x1171F ||
           (cp >= 0x11722 && cp <= 0x11725) ||
           (cp >= 0x11727 && cp <= 0x1172B) ||
           (cp >= 0x1182F && cp <= 0x11837) ||
            cp == 0x11839 ||
            cp == 0x1183A ||
            cp == 0x11930 ||
           (cp >= 0x1193B && cp <= 0x1193E) ||
            cp == 0x11943 ||
           (cp >= 0x119D4 && cp <= 0x119D7) ||
            cp == 0x119DA ||
            cp == 0x119DB ||
            cp == 0x119E0 ||
           (cp >= 0x11A01 && cp <= 0x11A0A) ||
           (cp >= 0x11A33 && cp <= 0x11A38) ||
           (cp >= 0x11A3B && cp <= 0x11A3E) ||
            cp == 0x11A47 ||
           (cp >= 0x11A51 && cp <= 0x11A56) ||
           (cp >= 0x11A59 && cp <= 0x11A5B) ||
           (cp >= 0x11A8A && cp <= 0x11A96) ||
            cp == 0x11A98 ||
            cp == 0x11A99 ||
           (cp >= 0x11C30 && cp <= 0x11C36) ||
           (cp >= 0x11C38 && cp <= 0x11C3D) ||
            cp == 0x11C3F ||
           (cp >= 0x11C92 && cp <= 0x11CA7) ||
           (cp >= 0x11CAA && cp <= 0x11CB0) ||
            cp == 0x11CB2 ||
            cp == 0x11CB3 ||
            cp == 0x11CB5 ||
            cp == 0x11CB6 ||
           (cp >= 0x11D31 && cp <= 0x11D36) ||
            cp == 0x11D3A ||
            cp == 0x11D3C ||
            cp == 0x11D3D ||
           (cp >= 0x11D3F && cp <= 0x11D45) ||
            cp == 0x11D47 ||
            cp == 0x11D90 ||
            cp == 0x11D91 ||
            cp == 0x11D95 ||
            cp == 0x11D97 ||
            cp == 0x11EF3 ||
            cp == 0x11EF4 ||
            cp == 0x11F00 ||
            cp == 0x11F01 ||
           (cp >= 0x11F36 && cp <= 0x11F3A) ||
           (cp >= 0x11F40 && cp <= 0x11F42) ||
            cp == 0x11F5A ||
            cp == 0x13440 ||
           (cp >= 0x13447 && cp <= 0x13455) ||
           (cp >= 0x1611E && cp <= 0x16129) ||
           (cp >= 0x1612D && cp <= 0x1612F) ||
           (cp >= 0x16AF0 && cp <= 0x16AF4) ||
           (cp >= 0x16B30 && cp <= 0x16B36) ||
            cp == 0x16F4F ||
           (cp >= 0x16F8F && cp <= 0x16F92) ||
            cp == 0x16FE4 ||
            cp == 0x16FF0 ||
            cp == 0x16FF1 ||
            cp == 0x1BC9D ||
            cp == 0x1BC9E ||
           (cp >= 0x1CF00 && cp <= 0x1CF2D) ||
           (cp >= 0x1CF30 && cp <= 0x1CF46) ||
           (cp >= 0x1D165 && cp <= 0x1D169) ||
           (cp >= 0x1D16D && cp <= 0x1D172) ||
           (cp >= 0x1D17B && cp <= 0x1D182) ||
           (cp >= 0x1D185 && cp <= 0x1D18B) ||
           (cp >= 0x1D1AA && cp <= 0x1D1AD) ||
           (cp >= 0x1D242 && cp <= 0x1D244) ||
           (cp >= 0x1DA00 && cp <= 0x1DA36) ||
           (cp >= 0x1DA3B && cp <= 0x1DA6C) ||
            cp == 0x1DA75 ||
            cp == 0x1DA84 ||
           (cp >= 0x1DA9B && cp <= 0x1DA9F) ||
           (cp >= 0x1DAA1 && cp <= 0x1DAAF) ||
           (cp >= 0x1E000 && cp <= 0x1E006) ||
           (cp >= 0x1E008 && cp <= 0x1E018) ||
           (cp >= 0x1E01B && cp <= 0x1E021) ||
            cp == 0x1E023 ||
            cp == 0x1E024 ||
           (cp >= 0x1E026 && cp <= 0x1E02A) ||
            cp == 0x1E08F ||
           (cp >= 0x1E130 && cp <= 0x1E136) ||
            cp == 0x1E2AE ||
           (cp >= 0x1E2EC && cp <= 0x1E2EF) ||
           (cp >= 0x1E4EC && cp <= 0x1E4EF) ||
            cp == 0x1E5EE ||
            cp == 0x1E5EF ||
           (cp >= 0x1E8D0 && cp <= 0x1E8D6) ||
           (cp >= 0x1E944 && cp <= 0x1E94A) ||
           (cp >= 0x1F3FB && cp <= 0x1F3FF) ||
           (cp >= 0xE0020 && cp <= 0xE007F) ||
           (cp >= 0xE0100 && cp <= 0xE01EF);
    }

    static boolean isConsonant(int cp) {
        // fast check - Devanagari to Malayalam
        if (cp < 0x0900 || cp > 0x0D7F) {
            return false;
        }

        return
           (cp >= 0x0915 && cp <= 0x0939) ||
           (cp >= 0x0958 && cp <= 0x095F) ||
           (cp >= 0x0978 && cp <= 0x097F) ||
           (cp >= 0x0995 && cp <= 0x09A8) ||
           (cp >= 0x09AA && cp <= 0x09B0) ||
            cp == 0x09B2 ||
           (cp >= 0x09B6 && cp <= 0x09B9) ||
            cp == 0x09DC ||
            cp == 0x09DD ||
            cp == 0x09DF ||
            cp == 0x09F0 ||
            cp == 0x09F1 ||
           (cp >= 0x0A95 && cp <= 0x0AA8) ||
           (cp >= 0x0AAA && cp <= 0x0AB0) ||
            cp == 0x0AB2 ||
            cp == 0x0AB3 ||
           (cp >= 0x0AB5 && cp <= 0x0AB9) ||
            cp == 0x0AF9 ||
           (cp >= 0x0B15 && cp <= 0x0B28) ||
           (cp >= 0x0B2A && cp <= 0x0B30) ||
            cp == 0x0B32 ||
            cp == 0x0B33 ||
           (cp >= 0x0B35 && cp <= 0x0B39) ||
            cp == 0x0B5C ||
            cp == 0x0B5D ||
            cp == 0x0B5F ||
            cp == 0x0B71 ||
           (cp >= 0x0C15 && cp <= 0x0C28) ||
           (cp >= 0x0C2A && cp <= 0x0C39) ||
           (cp >= 0x0C58 && cp <= 0x0C5A) ||
           (cp >= 0x0D15 && cp <= 0x0D3A);
    }
}
