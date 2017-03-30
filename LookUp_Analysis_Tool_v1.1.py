import os
import sys
import wx
from lxml import etree
import re
import time
from bs4 import BeautifulSoup
import platform
from datetime import datetime


'''
To the next developer. I apologise for the state of this. It was done in a rushed few days, as I was learning my first
programming language. Beautiful Soup was discovered towards the end, and the regex 'XML parsing' without this is horrific.
'''

versionNumber = 'v1.1'

systemType = platform.system()


def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] + list(chain(*([tostring(c, with_tail=False), c.tail]
                                        for c in node.getchildren()))) + [node.tail])
    return ''.join(filter(None, parts))
    

class ScrolledWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 140),
                          style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER |
                          wx.RESIZE_BOX | wx.MAXIMIZE_BOX))

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.Show()

        outputtxt3 = '''Drop iTunes Lookup ITMSP:'''
        wx.StaticText(self, -1, outputtxt3, pos=(7, 10), style=wx.ALIGN_CENTRE)

        self.drop_target = MyFileDropTarget(self)
        self.SetDropTarget(self.drop_target)
        self.tc_files = wx.TextCtrl(self, wx.ID_ANY, pos=(10, 40), size=(325, 25))

        self.buttonClose = wx.Button(self.panel, -1, "Close", pos=(5, 75))
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnClose)

        self.buttonSubmit = wx.Button(self.panel, -1, "Submit", pos=(150, 35), size=(180, 100))
        self.buttonSubmit.Bind(wx.EVT_BUTTON, self.parseXML)

    def parseXML(self, event):
        twoD_captions_list = []
        twoD_full_subs_list = []
        twoD_forced_subs_list = []
        twoD_HoH_subs_list = []
        twoD_audio_list = []

        for root, dirs, files in os.walk(self.dropFiles):
            for firstFile in files:
                if firstFile.endswith(".xml") and not firstFile.startswith("."):
                    filePath = os.path.join(root, firstFile)
                    with open(filePath) as f:
                        xml = f.readlines()
                        xml = ''.join(xml)
                        root = etree.fromstring(xml)
                        datafile_list = root.findall('.//data_file')

                        soup = BeautifulSoup(open(filePath), 'lxml')
                        bSoup_twoD_preview_list = []
                        for prev in soup.findAll(attrs={"type": "preview"}):
                            if prev.territory:
                                territory_list = [x for x in prev.territories.contents if x != u'\n']
                            else:  # WW PREVIEW
                                territory_list = []
                            preview_filename = prev.file_name.contents[0]
                            preview_audio_locale = prev.locale['name']

                            if prev('attribute', {'name': "image.burned_subtitles.locale"}):
                                preview_subs_locale = str(
                                    prev('attribute', {'name': "image.burned_subtitles.locale"})[0])
                                preview_subs_locale = re.sub('<attribute name="image.burned_subtitles.locale">', '',
                                                             preview_subs_locale)
                                preview_subs_locale = re.sub('</attribute>', '', preview_subs_locale)
                                subs_exist_var = 'Embedded subtitles: '
                            else:  # NO SUBS IN TRAILER
                                preview_subs_locale = '\t\t'
                                subs_exist_var = '-'

                            preview_listo = [preview_filename, preview_audio_locale, subs_exist_var,
                                             preview_subs_locale,
                                             territory_list]
                            bSoup_twoD_preview_list.extend([preview_listo])

                        for source in soup.findAll(attrs={"type": "full"}):
                            feature_filename = str(source.file_name.contents[0])
                            feature_locale = str(source.locale['name'])
                            feature_list = [feature_filename, feature_locale]

                        for elem in datafile_list:
                            try:
                                if elem.attrib["role"] == "captions":
                                    captions_block = stringify_children(elem)
                                    for each_line in captions_block.splitlines():
                                        if 'file_name' in each_line:
                                            filename_captions = re.sub('<file_name>', '', each_line)
                                            filename_captions = re.sub('</file_name>', '', filename_captions)
                                            filename_captions = re.sub(' ', '', filename_captions)
                                            filename_captions = re.sub('\n', '', filename_captions)
                                        if 'locale name' in each_line:
                                            audio_locale = re.sub('<locale name="', '', each_line)
                                            audio_locale = re.sub('"/>', '', audio_locale)
                                            audio_locale = re.sub(' ', '', audio_locale)
                                            audio_locale = re.sub('\n', '', audio_locale)
                                    captions_list = [elem.attrib["role"], filename_captions, audio_locale]
                                    twoD_captions_list.extend([captions_list])
                                if elem.attrib["role"] == "subtitles":
                                    subtitles_block = stringify_children(elem)
                                    for each_line in subtitles_block.splitlines():
                                        if 'file_name' in each_line:
                                            filename_full_subs = re.sub('<file_name>', '', each_line)
                                            filename_full_subs = re.sub('</file_name>', '', filename_full_subs)
                                            filename_full_subs = re.sub(' ', '', filename_full_subs)
                                            filename_full_subs = re.sub('\n', '', filename_full_subs)
                                        if 'locale name' in each_line:
                                            audio_locale = re.sub('<locale name="', '', each_line)
                                            audio_locale = re.sub('"/>', '', audio_locale)
                                            audio_locale = re.sub(' ', '', audio_locale)
                                            audio_locale = re.sub('\n', '', audio_locale)
                                    full_subs_list = [elem.attrib["role"], filename_full_subs, audio_locale]
                                    twoD_full_subs_list.extend([full_subs_list])
                                if elem.attrib["role"] == "forced_subtitles":
                                    forced_subtitles_block = stringify_children(elem)
                                    for each_line in forced_subtitles_block.splitlines():
                                        if 'file_name' in each_line:
                                            filename_forced_subs = re.sub('<file_name>', '', each_line)
                                            filename_forced_subs = re.sub('</file_name>', '', filename_forced_subs)
                                            filename_forced_subs = re.sub(' ', '', filename_forced_subs)
                                            filename_forced_subs = re.sub('\n', '', filename_forced_subs)
                                        if 'locale name' in each_line:
                                            audio_locale = re.sub('<locale name="', '', each_line)
                                            audio_locale = re.sub('"/>', '', audio_locale)
                                            audio_locale = re.sub(' ', '', audio_locale)
                                            audio_locale = re.sub('\n', '', audio_locale)
                                    forced_subs_list = [elem.attrib["role"], filename_forced_subs, audio_locale]
                                    twoD_forced_subs_list.extend([forced_subs_list])
                                if elem.attrib["role"] == "subtitles.hearing_impaired":
                                    HoH_subs_block = stringify_children(elem)
                                    for each_line in HoH_subs_block.splitlines():
                                        if 'file_name' in each_line:
                                            filename_HoH_subs = re.sub('<file_name>', '', each_line)
                                            filename_HoH_subs = re.sub('</file_name>', '', filename_HoH_subs)
                                            filename_HoH_subs = re.sub(' ', '', filename_HoH_subs)
                                            filename_HoH_subs = re.sub('\n', '', filename_HoH_subs)
                                        if 'locale name' in each_line:
                                            audio_locale = re.sub('<locale name="', '', each_line)
                                            audio_locale = re.sub('"/>', '', audio_locale)
                                            audio_locale = re.sub(' ', '', audio_locale)
                                            audio_locale = re.sub('\n', '', audio_locale)
                                    HoH_subs_list = [elem.attrib["role"], filename_HoH_subs, audio_locale]
                                    twoD_HoH_subs_list.extend([HoH_subs_list])
                                if elem.attrib["role"] == "audio":
                                    audio_block = stringify_children(elem)
                                    for each_line in audio_block.splitlines():
                                        if 'file_name' in each_line:
                                            filename_audio = re.sub('<file_name>', '', each_line)
                                            filename_audio = re.sub('</file_name>', '', filename_audio)
                                            filename_audio = re.sub(' ', '', filename_audio)
                                            filename_audio = re.sub('\n', '', filename_audio)
                                        if 'locale name' in each_line:
                                            audio_locale = re.sub('<locale name="', '', each_line)
                                            audio_locale = re.sub('"/>', '', audio_locale)
                                            audio_locale = re.sub(' ', '', audio_locale)
                                            audio_locale = re.sub('\n', '', audio_locale)
                                    audio_list = [elem.attrib["role"], filename_audio, audio_locale]
                                    twoD_audio_list.extend([audio_list])
                                else:
                                    pass
                            except:
                                pass

        dateTime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        vendorID = soup.vendor_id.contents[0]
        featureTitle = soup.title.contents[0]

        if systemType == "Darwin":
            OutputDoc = self.dropFiles + '/LookUpAnalysis_' + vendorID + '.txt'
        else:
            OutputDoc = self.dropFiles + '\\LookUpAnalysis_' + vendorID + '.txt'

        with open(OutputDoc, 'w') as text_doc:
            text_doc.write('// ' + dateTime + '\n' + '// ' + featureTitle + '\n' + '// ' + vendorID + '\n\n\n')
            text_doc.write(feature_list[0] + '\t\t\t' + 'Audio: ' + feature_list[1] + '\n\n')

            soup_preview_count = 0
            for soup_prev in bSoup_twoD_preview_list:
                if len(soup_prev[0]) < 25:
                    output_territory = str(soup_prev[4])
                    output_territory = re.sub('<territory>', '', output_territory)
                    output_territory = re.sub('</territory>', '', output_territory)
                    output_territory = re.sub('\[', '', output_territory)
                    output_territory = re.sub(']', '', output_territory)
                    text_doc.write(soup_prev[0] + '\t\t\t' + 'Audio: ' + soup_prev[1] + '\t\t'
                                   + soup_prev[2] + '\t' + soup_prev[3] + '\t\t' + output_territory
                                   + '\n')
                else:
                    output_territory = str(soup_prev[4])
                    output_territory = re.sub('<territory>', '', output_territory)
                    output_territory = re.sub('</territory>', '', output_territory)
                    output_territory = re.sub('\[', '', output_territory)
                    output_territory = re.sub(']', '', output_territory)
                    text_doc.write(soup_prev[0] + '\t\t' + 'Audio: ' + soup_prev[1] + '\t\t'
                                   + soup_prev[2] + '\t' + soup_prev[3] + '\t\t' + output_territory
                                   + '\n')
                soup_preview_count += 1
            text_doc.write('Previews count: ' + str(soup_preview_count) + '\n\n')

            caption_count = 0
            for captions in twoD_captions_list:
                caption_count += 1
                text_doc.write(captions[1] + '\t\t' + 'Full sub locale: ' + captions[2] + '\n')
            text_doc.write('Closed captions count: ' + str(caption_count) + '\n\n')

            subs_count = 0
            for fullSubs in twoD_full_subs_list:
                if len(fullSubs[2]) > 2:
                    print fullSubs[2]
                    subs_count += 1
                    text_doc.write(fullSubs[1] + '\t\t' + 'Full Sub locale: ' + fullSubs[2] + '\n')
                else:
                    subs_count += 1
                    text_doc.write(fullSubs[1] + '\t\t\t' + 'Full Sub locale: ' + fullSubs[2] + '\n')
            text_doc.write('Full subtitles count: ' + str(subs_count) + '\n\n')

            forced_count = 0
            for forcedSubs in twoD_forced_subs_list:
                forced_count += 1
                text_doc.write(forcedSubs[1] + '\t\t' + 'Forced sub locale: ' + forcedSubs[2] + '\n')
            text_doc.write('Forced subtitles count: ' + str(forced_count) + '\n\n')

            Hoh_count = 0
            for HoHsubs in twoD_HoH_subs_list:
                Hoh_count += 1
                text_doc.write(HoHsubs[1] + '\t' + 'SDH locale: ' + HoHsubs[2] + '\n')
            text_doc.write('SDH count: ' + str(Hoh_count) + '\n\n')

            audio_count = 0
            for altaudio in twoD_audio_list:
                audio_count += 1
                text_doc.write(altaudio[1] + '\t\t' + 'Audio locale: ' + altaudio[2] + '\n')
            text_doc.write('Alt audio count: ' + str(audio_count) + '\n\n')

        msg = wx.MessageDialog(self, "Your lookup analysis has been written to back to the ITMSP folder.\n\n" +
                               OutputDoc, "Awesome!", wx.OK | wx.ICON_INFORMATION)
        msg.ShowModal()
        msg.Close()

        print 'Status: Complete\nPlease check the document in ' + OutputDoc
        os.system("open " + OutputDoc)
        self.OnClose(ScrolledWindow)

    def setSubmissionDrop(self, dropFiles):
        self.listEmpty = False
        self.tc_files.SetValue(','.join(dropFiles))
        self.dropFiles = dropFiles[0]

    def OnClose(self, e):
        CloseApp()


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.setSubmissionDrop(filenames)

class CloseApp(wx.Frame):
    def __init__(e):
        sys.exit(0)


app = wx.App()
ScrolledWindow(None, -1, 'Look Up Analysis Tool ' + versionNumber)
app.MainLoop()
