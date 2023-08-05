#-*- coding: utf-8 -*-
import unittest
from language_detector import detect_language as dl
from language_detector import *

class TestStringMethods(unittest.TestCase):

    def test_arabic(self):
        text = """
        وجاء في بيان صادر عن مكتب رئيس الحكومة حيدر العبادي إن الخطوة التركية "انتهاك خطير للسيادة العراقية".

        """
        self.assertEqual(dl(text), "Arabic")

    def test_french(self):
        text = """
        Trois assaillants ont été tués et deux autres arrêtés vendredi à Bujumbura après avoir tendu une embuscade à Christophe Manirambona, chef du bureau des unités spécialisées, un haut responsable de la police qui n'était pas dans son véhicule.
        """
        self.assertEqual(dl(text), "French")

    def test_english(self):
        text = """
        JEM Raw is recalling nut butters after health officials found a likely link to a salmonella outbreak. 82 Shares. Email. A salmonella outbreak linked to an organic line of nut butters has sickened 11 people according to the Centers for Disease Control 
        """
        self.assertEqual(dl(text), "English")

    def test_kurmanci(self):
        text = """
        Luv xelata xwe pêşkêşî 55 milyon kurd û pêşmergeyan kir Zêdetir
        """
        self.assertEqual(dl(text), "Kurmanci")

    def test_sorani(self):
        text = """
        22:18 | دەمیرتاش: كورد گەیشتووەتە "خاڵێكی مەزن" بۆ راگەیاندنی دەوڵەتی خۆی
        """
        self.assertEqual(dl(text), "Sorani")

    def test_turkish(self):
        text = """
        Amerikan Federal Soruşturma Bürosu (FBI), ABD'nin Kaliforniya Eyaleti'nde Çarşamba günü gerçekleştirilen ve 14 kişinin yaşamını yitirdiği saldırının 'terörizm eylemi' olarak inceleneceğini söyledi.
        """
        self.assertEqual(dl(text), "Turkish")

    def test_english_iterable(self):
        iterable = ["Washington", "Adams", "Jefferson"]
        self.assertEqual(dl(iterable), "English")

    def test_is_english(self):
        text = "Bla bla bla I'm not sure where to start."
        self.assertEqual(isEnglish(text), True)

if __name__ == '__main__':
    unittest.main()
