#!/usr/bin/env python
'''
Created on 27 Nov 2015

@author: uwe
'''

import sys,getopt
from copy import deepcopy
from LyMaker.ScaleUtil import ScaleUtil,Scale,ChordProgressions

VERSION = "0.5.4"


class Part(object):
    def __init__(self):
        self.name = ""
        self.drummode  = 0
        self.groove = 0
        self.melody = 0
        self.harmony = 0
        self.tempo = 0
        self.progressions = ""
        self.percussion = 99
        self.poly = 0
        self.percbeat = 0

class Chordhelper(object):
    
    def transform(self,input):
        output = []
        bars = input.split('|')
        for b in bars:
            bar = []
            chords = b.split(';')
            for chord in chords:
                base = ""
                ext = ""
                flat = False
                if len(chord) > 2 and chord[1:3] == 'is':
                    #print "sharp chord"
                    base = chord[:3]
                    if len(chord) > 3:
                        ext = chord[3:]
                elif len(chord) > 1 and chord[1:2] == '#':
                    #print "sharp chord"
                    base = chord[:1]
                    base += "is"
                    if len(chord) > 2:
                        ext = chord[2:]
                elif len(chord) > 2 and chord[1:3] == 'es':
                    flat = True
                    #print "flat chord"
                    base = chord[:3]
                    if len(chord) > 3:
                        ext = chord[3:]
                elif len(chord) > 1 and chord[1:2] == 's':
                    #print "sharp chord es,as"
                    flat = True
                    base = chord[:2]
                    if len(chord) > 2:
                        ext = chord[2:]
                elif len(chord) > 1 and chord[1:2] == 'b':
                    #print "flat chord"
                    flat = True
                    base = chord[:1]
                    if base == 'a' or base == 'e':
                        base += "s"
                    else:
                        base += "es"
                    if len(chord) > 2:
                        ext = chord[2:]
                else:
                    #print "normal chord"
                    base = chord[:1]
                    ext = chord[1:]
                idx,flat = ScaleUtil.getNoteFromName(base)         
                if idx == -1:    
                    print "I don't know this chord: %s base: %s" % (input,base)
                    continue
                notes = self._getNotes(idx,ext)
                ch = []
                for n in notes:
                    name = Scale.getNoteName(n,flat)
                    ch.append(deepcopy(name))
                bar.append(deepcopy(ch))    
            output.append(deepcopy(bar))
        return output

    def _getNotes(self,idx,ext):
        offset1 = 4
        offset2 = 7
        offset3 = 0

        # major
        if ext == "b13":
            offset3 = 8
        elif ext == "6":
            offset3 = 9
        elif ext == "7":
            offset3 = 10
        elif ext == "maj7":
            offset3 = 11
        elif ext == "add9":
            offset3 = 14
        elif ext == "add11":
            offset3 = 17
        elif ext == "7b13/5-":
            offset2 = 6
            offset3 = 8
        elif ext == "7/5-":
            offset2 = 6
            offset3 = 10
        elif ext == "maj7/5-":
            offset2 = 6
            offset3 = 11
        elif ext == "6/5+":
            offset2 = 8
            offset3 = 9
        elif ext == "7/5+":
            offset2 = 8
            offset3 = 10
        elif ext == "maj7/5+":
            offset2 = 8
            offset3 = 11
        elif ext == "6/9":
            offset2 = 9
            offset3 = 14
        

        # minor, dim
        elif ext == "m":
            offset1 = 3
        elif ext == "mb13":
            offset1 = 3
            offset3 = 8
        elif ext == "m6":
            offset1 = 3
            offset3 = 9
        elif ext == "m7":
            offset1 = 3
            offset3 = 10
        elif ext == "mmaj7":
            offset1 = 3
            offset3 = 11
        elif ext == "m7/5-":
            offset1 = 3
            offset2 = 6
            offset3 = 10
        elif ext == "madd9":
            offset1 = 3
            offset3 = 14
        elif ext == "madd11":
            offset1 = 3
            offset3 = 17
        elif ext == "dim7":
            offset1 = 3
            offset2 = 6
            offset3 = 9
            
        # sus4
        elif ext == "sus4":
            offset1 = 5
        elif ext == "b13sus4":
            offset1 = 5
            offset3 = 8
        elif ext == "6sus4":
            offset1 = 5
            offset3 = 9
        elif ext == "7sus4":
            offset1 = 5
            offset3 = 10
        elif ext == "maj7sus4":
            offset1 = 5
            offset3 = 11
        elif ext == "add9sus4":
            offset1 = 5
            offset3 = 14
        elif ext == "add11sus4":
            offset1 = 5
            offset3 = 17

        # sus2
        elif ext == "sus2":
            offset1 = 2
        elif ext == "b13sus2":
            offset1 = 2
            offset3 = 8
        elif ext == "6sus2":
            offset1 = 2
            offset3 = 9
        elif ext == "7sus2":
            offset1 = 2
            offset3 = 10
        elif ext == "maj7sus2":
            offset1 = 2
            offset3 = 11
        elif ext == "add9sus2":
            offset1 = 2
            offset3 = 14
        elif ext == "add11sus2":
            offset1 = 2
            offset3 = 17

        # other triads
        elif ext == "dim":
            offset1 = 3
            offset2 = 6
        elif ext == "aug":
            offset1 = 4
            offset2 = 8
        elif ext == "b5":
            offset2 = 6
        elif ext == "5":
            offset1 = 7
            offset2 = 12
        elif ext == "":
            pass
        else:
            print "I don't know the chord variant %s" % ext

        notes = []
        notes.append(deepcopy(idx))
        idx2 = 0
        if idx + offset1 < 12:
            idx2 = idx + offset1
            notes.append(deepcopy(idx2))
        else:
            idx2 = offset1 -(12 -idx)
            notes.append(deepcopy(idx2))

        idx3 = 0
        if idx2 + offset2 - offset1 < 12:
            idx3 = idx2 + offset2 - offset1
            notes.append(deepcopy(idx3))
        else:
            idx3 = (offset2 - offset1) -(12 -idx2)
            notes.append(deepcopy(idx3))

        idx4 = 0
        if offset3 and idx3 + offset3 - offset2 < 12:
            idx4 = idx3 + offset3 - offset2
            notes.append(deepcopy(idx4))
        elif offset3:
            idx4 = (offset3 -  offset2) -(12 -idx3)
            notes.append(deepcopy(idx4))
        return notes

class LyWizard(object):

    def __init__(self,chordhelper):
        self.parts = []
        self.chordhelper = chordhelper
        self.part = None
        
        self.quarters = 4
        self.eighths = 0
        self.tempo = 120
        self.name = ""
        self.downbeats ="1,3"  
        self.key = "c major"
        self.structure = ""
        self.onbeat = 0 # offbeat
        self.harmoniesStaff = 0 # bass staff
        self.synthMode = 0 #0 = sax,trumpet & piano, 1 = all synths
        self.drumsAsInstr = 0 #1 = drums as separate instruments

    def process(self):
        self._header()
        adding = 1
        while adding:
            p = Part()
            self._part(p)
            self.parts.append(p)
            adding =  self._getInput("Do you want to add another part? [y]:",self._yesNoCheck,self._transYesNo,"answer with y or n")   
        defaultStructure = self._getDefaultStructure()    
        question = "Enter the structure of your song [%s]:" % defaultStructure
        self.structure =  self._getInput(question,self._checkStructure,self._transStructure,"use only A-Z and only so many characters as you have parts")   
        xml = self._asXml()
        outx = None
        try:
            outx = open(self.name + ".xml","w")
        except:
            print "Cannot open %s" % (filename + ".xml")
        if outx:    
            outx.write(xml)
            outx.flush()
            outx.close

    def _asXml(self):
        try:
            text = "<LyMk>\n"
            text += "<version>%s</version>\n" % VERSION
            text += "<song>\n<name>%s</name>\n" % self.name
            numerator = 4
            denominator = 4
            if self.quarters > 0:
                numerator = self.quarters
            else:
                numerator = self.eighths
                denominator = 8
            text += "<time>%d,%d</time>\n" % (numerator,denominator)
            text += "<key>%s</key>\n" % self.key
            text += "<tempo>%d</tempo>\n" % self.tempo
            text += "<structure>%s</structure>\n" % self.structure
            text += "<downbeats>%s</downbeats>\n" % self.downbeats
            text += "<onbeat>%d</onbeat>\n" % self.onbeat
            text += "<harmoniesStaff>%d</harmoniesStaff>\n" % self.harmoniesStaff
            text += "<synthMode>%d</synthMode>\n" % self.synthMode
            text += "<drumsAsInstr>%d</drumsAsInstr>\n" % self.drumsAsInstr
            i = 0
            count = len(self.parts)
            while i < count:
                part = self.parts[i]
                text += "<part>\n"
                text += "<partname>%s</partname>\n" % part.name
                if part.tempo != self.tempo and part.tempo > 0:
                    text += "<ptempo>%d</ptempo>\n" % part.tempo
                text += "<progressions>%s</progressions>\n" % part.progressions
                text += "<groove>%d</groove>\n" % part.groove
                text += "<drummode>%d</drummode>\n" % part.drummode
                text += "<poly>%d</poly>\n" % part.poly
                text += "<harmony>%d</harmony>\n" % part.harmony
                text += "<melody>%d</melody>\n" % part.melody
                text += "<percussion>%d</percussion>\n" % part.percussion 
                text += "<percbeat>%d</percbeat>\n" % part.percbeat 
                text += "</part>\n"
                i += 1
            text += "</song>\n"
            text += "</LyMk>"
            return text
        except Exception as e:
            print "Exception in _asXml %s\n" % e
            print text
            return None

    def _getInput(self,message,checkroutine,transform,hint):
        ok = False
        while ok is False:
            input = raw_input(message)
            if input == "help" or input == "h" or input == "?":
                print hint
                ok = False
            else:    
                ok = checkroutine(input)
                if ok == False:
                    print hint
        return transform(input)    

    def _getDefaultStructure(self):
        if len(self.parts) == 1:
            output = "AAAAAAAAAAAA"
        elif len(self.parts) == 2:
            output = "ABABABABABAB"
        elif len(self.parts) == 3:
            output = "ABABABABABACB"
        elif len(self.parts) == 4:
            output =  "ABCBCBCBCBCBCBDC"
        elif len(self.parts) > 4:
            output = "ABCBCBCBCBCBCBDCE"
        return output    
    

    def _checkEmpty(self,input):
        if len(input):
            return True
        else:
            return False

    def _checkProgressions(self,input):
        input = input.strip()
        if len(input):
            if self.chordhelper == False and input.find(",") == -1:
                print "no comma detected, notes must be separated by comma in single note mode"
                return False
            elif self.chordhelper == True and input.find(",") != -1:
                print "no comma allowed in chord mode"
                return False
            if input.find(".") != -1:
                print "dots are not allowed"
                return False
            if input.find(" ") != -1:
                print "spaces are not allowed"
                return False
            return True
        else:
            return False

    def _checkStructure(self,input):
        if len(input):
            for c in input:
                if ord(c) < ord(A) or ord(c) > ord(Z):
                    return False
                elif ord(c) - ord(A) >= len(self.parts):
                    return False
            return True
        else:
            return True

    def _checkMelody(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 6:
                return True
            else:
                return False
        else:
            return True

    def _checkFeel(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 12:
                return True
            else:
                return False
        else:
            return True

    def _checkPFeel(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 11:
                return True
            else:
                return False
        else:
            return True

    def _checkHarmony(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 8:
                return True
            elif int(input) == 99:
                return True
            else:
                return False
        else:
            return True

    def _checkGroove(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 6:
                return True
            elif int(input) == 99:
                return True
            else:
                return False
        else:
            return True

    def _checkDrums(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 6:
                return True
            elif int(input) == 99:
                return True
            else:
                return False
        else:
            return True

    def _checkPercussion(self,input):
        if len(input):
            if int(input) >= 0 and int(input) < 4:
                return True
            elif int(input) == 99:
                return True
            else:
                return False
        else:
            return True

    def _yesNoCheck(self,input):
        if len(input):
            if input == 'y':
                return True
            if input == 'n':
                return True
            else:
                return False
        else:
            return True

    def _checkTempo(self,input):
        if len(input):
            output = int(input)
        else:
            output = 100
        if output > 19 and output < 201:
            return True
        else:
            return False    

    def _transTempo(self,input):
        if len(input):
            output = int(input)
        else:
            output = 100
        return output    

    def _transTempoPart(self,input):
        if len(input):
            output = int(input)
        else:
            output = 0
        return output    
    
    def _noCheck(self,input):
        return True

    def _noAction(self,input):
        return input

    def _transAsInt(self,input):
        if len(input):
            return int(input)
        else:
            return 0

    def _checkSignature(self,input):
        if len(input) == 0:
            return True
        sig1,sig2 =  input.split('/')
        if len(sig1) and len(sig2):
            sig = int(sig2)
            if sig == 8:
                sig = int(sig1)
                if sig in [3,4,6,9,12]:
                    return True
                else:
                    return False
            elif sig == 4:
                sig = int(sig1)
                if sig in [2,3,4,6,7,9,10,11,12,16]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def _transSignature(self,input):
        if len(input) == 0:
            return 4,4
        sig1,sig2 =  input.split('/')
        if len(sig1):
            output1 = int(sig1)
        else:
            output1 = 4
        if len(sig2):
            output2 = int(sig2)
        else:
            output2 = 4
        return output1,output2    

    def _checkDownbeats(self,input):
        if len(input) == 0:
            input = self._downbeats()

        beats =  input.split(',')
        if self.eighths > 0:
            if len(beats) == 0 or len(beats) > self.eighths:
                return False
        else:    
            if len(beats) == 0 or len(beats) > self.quarters:
                return False
        for b in beats:
            c = int(b) # test value
        return True

    def _transDownbeats(self,input):
        if len(input):
            output =  input
        else:
            output = self._downbeats()
        return output    

    def _transChords(self,input):
        if input == 'r':
            note,sc,flat = ScaleUtil.getScaleFromString(self.key)
            scale = Scale()
            scale.initialize(note,sc,flat)
            beats = self.downbeats.split(',')
            chpg = ChordProgressions(scale,len(beats))
            output = chpg.generate()
            return output
        if self.chordhelper == False:
            output =  input
        else:
            output = ""
            ch = Chordhelper()
            chords = ch.transform(input)
            for bar in chords:
                if len(output):
                    output += "|"
                for chord in bar:
                    if len(output) and output[len(output)-1] != '|':
                        output += ";"
                    for note in chord:
                        if len(output) and output[len(output)-1] != ';' and output[len(output)-1] != '|':
                            output += ","
                        output += note
        return output    

    def _transStructure(self,input):
        if len(input):
            output =  input
        else:
            output = self._getDefaultStructure()
        return output    

    def _transYesNo(self,input):
        if len(input):
            if input == 'y':
                return 1
            else:
                return 0
        else:
            return 1

    def _downbeats(self):
        beats = "1,3"
        if self.quarters != 0:
            if self.quarters < 4:
                beats = "1" # simple duple or triple
            elif self.quarters < 6:
                beats = "1,3"
            elif self.quarters == 6:
                beats = "1,4" # 3-3 compound duple
            elif self.quarters == 7:
                beats = "1,3,5" # 2-2-3 compound triple
            elif self.quarters == 8:
                beats = "1,3,5,7" # 2-2-2-2 compound quadruple
            elif self.quarters == 9:
                beats = "1,4,7" # 3-3-3 compound triple
            elif self.quarters == 10:
                beats = "1,3,6,8" # indian jhaptaal
            elif self.quarters == 11:
                beats = "1,4,8" # awiis
            elif self.quarters == 12:
                beats = "1,3,5,7,9,11" # indian ektaal
            elif self.quarters == 16:
                beats = "1,5,9,13" # indian teentaal
        else:
            if self.eighths < 4:
                beats = "1"
            elif self.eighths == 4:
                beats = "1,3"
            elif self.eighths < 9:
                beats = "1,4"
            elif self.eighths == 9:
                beats = "1,4,7"
            elif self.eighths < 12:
                beats = "1,4,7"
            elif self.eighths == 12:
                beats = "1,4,7,10"

        return beats

    def _header(self):
        self.name = self._getInput("Enter the name of the song:",self._checkEmpty,self._noAction,"Name must not be empty")
        self.tempo = self._getInput("Enter the tempo of the song [100]:",self._checkTempo,self._transTempo,"Tempo must be between 20 and 200")
        self.key = self._getInput("Enter the key of the song [c major]:",self._noCheck,self._noAction,"c,cis,d,dis,e,f,fis,g,gis,a,ais,b major/minor/dorian/aeolian/lydian,mixolydian,phrygian,locrian or twelve-tone")
        if len(self.key) == 0:
            self.key = "c major"
        sig1,sig2 = self._getInput("Enter the signature of the song [4/4]:",self._checkSignature,self._transSignature,"2-12/4,16/4,3/8,4/8,6/8,9/8,12/8")
        if sig2 == 8:
            self.eighths = sig1
            self.quarters = 0
        else:
            self.quarters = sig1
            self.eighths = 0
        beats = self._downbeats()

        text = "Enter the downbeats of the song ["
        text += beats
        text += ']'
        self.downbeats =  self._getInput(text,self._checkDownbeats,self._transDownbeats,"enter the downbeats of the song separated by comma,e.g 1,3 for 4/4")   
        self.onbeat =  self._getInput("Onbeat rhythm? [y]:",self._yesNoCheck,self._transYesNo,"answer with y or n")   
        self.synthMode =  self._getInput("Switch on synth mode? [y]:",self._yesNoCheck,self._transYesNo,"answer with y or n")   
        self.harmoniesStaff =  self._getInput("Move harmonies one octave up to violin staff? [y]:",self._yesNoCheck,self._transYesNo,"answer with y or n")   
        self.drumsAsInstr =  self._getInput("Drums as separate instruments? [y]:",self._yesNoCheck,self._transYesNo,"answer with y or n")   

    def _part(self,part):
        part.name = self._getInput("Enter the name of the part:",self._checkEmpty,self._noAction,"Name must not be empty")
        part.tempo = self._getInput("Enter the tempo of the part [0]:",self._noCheck,self._transTempoPart,"Tempo must be between 20 and 200 or 0 if the tempo is not different from the song tempo")
        part.melody = self._getInput("Enter the melody mode of the part [0]:",self._checkMelody,self._transAsInt,"0 = no melody, 1 = piano with counterpoint, 2 = trumpet with sax counterpoint, 3 = trumpet solo, 4 = sax solo, 5 = sax with piano counterpoint")
        part.harmony = self._getInput("Enter the harmony mode of the part [0]:",self._checkHarmony,self._transAsInt,"0 = chords on downbeat, 1 = arpeggio (NoteUp), 2 = arpeggio (NoteDown), 3 = arpeggio (Random), 4 = arpeggio (BarUpDown), 5 = arpeggio (BarDownUp), 6 = chords on downbeats, no riff, 7 = riff uses chords, 99 = mute")
        if self.onbeat:
            hint = "0 = ostinato half-time, 1 = walking bass, 2 = ostinato normal-time, 3 = ostinato double-time, 4 = shuffle, 5 = riff, 99 = mute"
        else:
            hint = "0 = funky, 1 = walking bass, 2,3  = random, 4 = shuffle, 5 = riff, 99 = mute"
        part.groove = self._getInput("Enter the bass mode of the part [0]:",self._checkGroove,self._transAsInt,hint)
        if self.onbeat:
            hint = "0 = backbeat, 1 = half-time, 2 = ride only, 3 = snare only, 4 = funky, 5 = drumpattern, 99 = mute"
        else:
            hint = "0 = random, 1 = random with less ride and snare, 2  = ride only, 3 = random without bass drum, 4 = funky, 5 = drumpattern, 99 = mute"
        part.drummode = self._getInput("Enter the drum mode of the part [0]:",self._checkDrums,self._transAsInt,hint)
        hint = "0 = random, 1 = light swing, 2  = medium swing, 3 = hard swing"
        if self.quarters == 4:
            hint += ", 4 = 3 over 2 quarters, 5 = 3 over 2 seminotes, 6 = 5 over 4, 7 = 7 over 4, 8 = 11 over 4, 9 = 13 over 4, 10 = 2-3 clave, 11 = 3-2 clave" 
        part.poly = self._getInput("Enter the feel of drum part [0]:",self._checkFeel,self._transAsInt,hint)
        part.percussion = self._getInput("Enter the percussion mode of the part [0]:",self._checkPercussion,self._transAsInt,"0 = bongo, 1 = conga, 2 = bongo as instrument, 3 = conga as instrument, 99 = mute")
        if self.quarters == 4:
            hint = "0 = random,1 2-3 clave, 2 = 3-2 clave,3 = 3 over 2 eighths, 4 = 3 over 2 quarters, 5 = 3 over 2 seminotes, 6 = 5 over 4, 7 = 7 over 4, 8 = 11 over 4, 9 = 13 over 4, 10 = basic bongo or conga beat " 
            part.percbeat = self._getInput("Enter the feel of percussion part [0]:",self._checkPFeel,self._transAsInt,hint)
        else:
            part.percbeat = 0
        if self.chordhelper == False:
            part.progressions = self._getInput("Enter the progressions for the part, notes separated by comma, chords separated by semicolon, bars separated by | no spaces:",self._checkProgressions,self._transChords,"Enter at least one chord or r for random chords, e.g. c,e,g or c,e,g;d,f,a|e,g,b\nUse Dutch note names e.g. bes or ais (lilypond default)!")
        else:
            part.progressions = self._getInput("Enter the progressions for the part, chordnames separated by semicolon, bars separated by | no spaces:",self._checkProgressions,self._transChords,"Enter at least one chord or r for random chords, e.g. c or c;dm|g6/9\nSupported are all chords that are listed in the LyMaker documentation. Use English or Dutch note names e.g. bes/bb or ais/a#!")



def usage():
    print "LyWizard.py -n"
    print "n = switch chord mode off and single note mode on, enter all notes for chords manually, e.g. c,e,g"
    print "In chord mode you can type in chord names, e.g. cmaj7"
    print "The chord mode knows only chords with 3 or 4 notes\n"

if __name__ == '__main__':
    print "LyWizard Version 0.0.2 beta"
    chordhelper = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "nh", ["notes","help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-n", "--notes"):
            chordhelper = False

    app = LyWizard(chordhelper)
    app.process()

