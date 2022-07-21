import regex
import re
import os


class Subtitle:
    persian_alpha_codepoints = '\u200c\u0621-\u0628\u062A-\u063A\u0641-\u0642\u0644-\u0648\u064E-\u0651\u0655\u067E\u0686\u0698\u06A9\u06AF\u06BE\u06CC'
    nums = "۰۱۲۳۴۵۶۷۸۹0123456789"

    def __init__(self, path: str):
        self.path = path
        if(path[-4:] == ".srt"):
            path = self.srt2ass(path)
        self.sub = open(path, encoding="utf-8").read()
        self.styles = [x.groups()[0] for x in regex.finditer(
            "(^Style: .*\n)", self.sub, flags=regex.MULTILINE)]
        self.fonts = [x.groups()[0] for x in regex.finditer(
            "(?:^Style: [^,]*),([^,]*),", self.sub, flags=regex.MULTILINE)]
        self.events = [x.groups()[0] for x in regex.finditer(
            "(^Dialogue: .*\n)", self.sub, flags=regex.MULTILINE)]
        self.sub = regex.sub("Dialogue: (?s).*",
                             "😕Dialogues_Place_Here😕", self.sub)
        self.sub = regex.sub(
            "\n(Style: (?s).*Style: [^(\n)]*)", r"\n🗿Styles_Place_Here🗿", self.sub)

    def export(self, dst):
        self.sub = self.sub.replace(
            "🗿Styles_Place_Here🗿", "".join(self.styles))
        self.sub = self.sub.replace(
            "😕Dialogues_Place_Here😕", "".join(self.events))
        with open(dst, "w", encoding="utf-8") as f:
            f.write(self.sub)

    def numbers_bug_fixer(self):
        bad_lines = []
        for i, event in enumerate(self.events):
            parts = event.split(",")
            before_text = ",".join(parts[:9])
            text = ",".join(parts[9:])
            is_badline = False
            new_text = list(text)
            nums_idx = [x.span()[0] for x in regex.finditer(
                "(?:}}|(\\\\N)|^)[^{{{0}]*([{1}]+)[{0}]+".format(Subtitle.persian_alpha_codepoints, Subtitle.nums), text)]
            for num_idx in nums_idx:
                if(text[num_idx] not in Subtitle.nums):
                    num_idx += 1
                new_text.insert(num_idx, "\u202b")
                is_badline = True
            if(is_badline):
                bad_lines.append(f"{parts[1]} --> {parts[2]}\n{text}")
                text = "".join(new_text)
            if(text != ""):
                self.events[i] = f"{before_text},{text}"
        return "\n".join(bad_lines)

    def nonb_farsifont_bug_fixer(self):
        bad_fonts = []
        Bfarsi_fonts = ['B Alok','B Arabic Style','B Arash','B Araz','B Aria','B Arshia','B Aseman',
        'B Badkonak','B Badr','B Baran','B Baran Outline','B Bardiya','B Cheshmeh','B Chini','B Compset',
        'B Davat','B Elham','B Elm','B Elm Border','B Esfehan','B Fantezy','B Farnaz','B Ferdosi',
        'B Haleh','B Hamid','B Helal','B Homa','B Jadid','B Jalal','B Johar',
        'B Kaj','B Kamran','B Kamran Outline','B Karim','B Kaveh','B Kidnap','B Koodak','B Koodak Outline','B Kourosh',
        'B Lotus','B Mah','B Mahsa','B Majid Shadow','B Mashhad','B Masjed','B Medad','B Mehr','B Mitra','B Moj','B Morvarid',
        'B Narenj','B Narm','B Nasim','B Nazanin','B Nazanin Outline','B Niki Border','B Niki Outline','B Niki Shadow','B Nikoo',
        'B Paatch','B Rose','B Roya','B Sahar','B Sahra','B Sara','B Sepideh','B Sepideh Outline','B Setareh',
        'B Shadi','B Shekari','B Shiraz','B Siavash','B Sina','B Sooreh','B Sorkhpust',
        'B Tabassom','B Tanab','B Tawfig Outline','B Tehran','B Tir','B Titr','B Titr TG E','B Traffic',
        'B Vahid','B Vosta','B Yagut','B Yas','B Yekan','B Zaman','B Zar','B Ziba']
        for i, style in enumerate(self.styles):
            parts = style.split(",")
            font = parts[1]
            if(f"B {font}" in Bfarsi_fonts):
                parts[1] = f"B {font}"
                self.styles[i] = ",".join(parts)
                bad_fonts.append(f"{font} --> {parts[1]}")
        return "\n".join(set(bad_fonts))

    def auto_sync(self, ref):
        for track in range(5):
            sample=[]
            os.popen(
                f"ffmpeg -y -i \"{ref}\" -map 0:s:{track} eng_anime_sub.ass")
            ffs_output=os.popen(
                f"ffs \"{ref}\" -i \"{self.path}\" -o \"{self.path[:-4]}_synced.ass\" ").read()
            total = 0
            correct = 0
            clk = "[0-6]{2}"
            with open(f"{self.path[:-4]}_synced.ass", encoding="utf-8")as f:
                sub_fa = f.read()
            with open(f"eng_anime_sub.ass", encoding="utf-8")as f:
                sub_en = f.read()
            for minute in ["0[1-5]", "0[5-9]", "1[0-5]", "1[5-9]", "2[0-5]"]:
                fa = [x.groups() for x in regex.finditer(
                    f"^Dialogue: [0-9]*,([0-2]:{minute}:{clk}\.[0-9]{{2}}),([0-2]:{clk}:{clk}\.[0-9]{{2}}).*,(.*)\n", sub_fa, flags=regex.MULTILINE)]
                for s, e, t in fa[:8]:
                    total += 1
                    en = [x.groups() for x in regex.finditer(
                        f"^Dialogue: [0-9]*,({s[:7]}\.[0-9]{{2}}),([0-2]:{clk}:{clk}\.[0-9]{{2}}).*,(.*)\n", sub_en, flags=regex.MULTILINE)]
                    if(len(en) == 0):
                        continue
                    correct += 1
                    sample.append(f"\nStart: {s}, end: {e} text: {t}")
                    for s2,e2,t2 in en[:3]:
                        sample.append(f"Start: {s2}, end: {e2} text: {t2}")
                sample.append(f"******")
            sync_score = round((correct/total)*100, 2)

            if(sync_score > 60):
                self.__init__(f"{self.path[:-4]}_synced.ass")
                sample.append(f"میزان تقریبی هماهنگ بودن زیرنویس : %{sync_score}")
                return "\n".join(sample)
        return "متاسفانه زیرنویس هماهنگ نشد"

    @staticmethod
    def srt2ass(input_file):
        src = ""
        encodings = ["utf-8", "cp1256"]
        for enc in encodings:
            try:
                with open(input_file, encoding=enc) as fd:
                    src = fd.read()
                    break
            except Exception:
                pass

        src = src.replace("\r", "")
        lines = [x.strip() for x in src.split("\n") if x.strip()]
        subLines = ''
        tmpLines = ''
        lineCount = 0
        output_file = '.'.join(input_file.split('.')[:-1])
        output_file += '.ass'

        for i, line in enumerate(lines):
            if line.isdigit() and re.match('-?\d\d:\d\d:\d\d', lines[(i+1)]):
                if tmpLines:
                    subLines += tmpLines + "\n"
                tmpLines = ''
                lineCount = 0
                continue
            else:
                if re.match('-?\d\d:\d\d:\d\d', line):
                    line = line.replace('-0', '0')
                    tmpLines += 'Dialogue: 0,' + line + ',Default,,0,0,0,,'
                else:
                    if lineCount < 2:
                        tmpLines += line
                    else:
                        tmpLines += f'\\N {line}'
                lineCount += 1

        subLines += tmpLines + "\n"

        subLines = re.sub(r'\d(\d:\d{2}:\d{2}),(\d{2})\d', '\\1.\\2', subLines)
        subLines = re.sub(r'\s+-->\s+', ',', subLines)
        # replace style
        subLines = re.sub(r'<([ubi])>', "{\\\\\g<1>1}", subLines)
        subLines = re.sub(r'</([ubi])>', "{\\\\\g<1>0}", subLines)
        subLines = re.sub(
            r'<font\s+color="?#(\w{2})(\w{2})(\w{2})"?>', "{\\\\c&H\\3\\2\\1&}", subLines)
        subLines = re.sub(r'</font>', "", subLines)
        default_style="Style: Default,B Koodak,30,&H00FFFFFF,&H0300FFFF,&H00000000,&H02000000,0,0,0,0,100,100,0,0,1,1.5,1,2,10,10,10,1"

        head_str = "[Script Info]\n; AnimWorld\nTitle:\nScriptType: v4.00+\nCollisions: Normal\nPlayDepth: 0\n"\
            "\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Ita lic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle,BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"\
            f"{default_style}\n\n[Events]\nFormat: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text"

        with open(output_file, 'w', encoding="utf-8") as output:
            output.write(f"{head_str}\n{subLines}")

        return output_file.replace('\\', '\\\\').replace('/', '//')
