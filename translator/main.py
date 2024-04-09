import csv
import os
import re
import pandas as pd

class DictionaryFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def _file_exists(self):
        return os.path.exists(self.file_path)

    def load_dictionary(self):
        dictionary = {}
        if self._file_exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        word = row[0].strip()
                        translation = row[1].strip()
                        if word not in dictionary:
                            dictionary[word] = [translation]
                        else:
                            dictionary[word].append(translation)
            except (FileNotFoundError, IOError) as e:
                print(f"Error loading dictionary: {e}")
        return dictionary

    def save_dictionary(self, dictionary):
        try:
            with open(self.file_path, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for word, translations in dictionary.items():
                    for translation in translations:
                        writer.writerow([word, translation])
        except IOError as e:
            print(f"Error saving dictionary: {e}")

    def export_dictionary_to_excel(self, dictionary):
        try:
            dataframe = pd.DataFrame.from_dict(dictionary, orient='index', columns=['Translation'])
            excel_file = os.path.splitext(self.file_path)[0] + ".xlsx"
            dataframe.to_excel(excel_file)
            print(f"Dictionary exported to {excel_file} successfully!")
        except Exception as e:
            print(f"Error exporting dictionary to Excel: {e}")


class Translator:
    def __init__(self, dictionary_file):
        self.dictionary_file = DictionaryFile(dictionary_file)
        self.dictionary = self.dictionary_file.load_dictionary()
        self.translation_history = []

    def update_dictionary(self, word, translations):
        if word in self.dictionary:
            self.dictionary[word].extend(translations)
        else:
            self.dictionary[word] = translations
        self.dictionary_file.save_dictionary(self.dictionary)

    def delete_translation(self, word, translation):
        if word in self.dictionary and translation in self.dictionary[word]:
            self.dictionary[word].remove(translation)
            if not self.dictionary[word]:
                del self.dictionary[word]
            self.dictionary_file.save_dictionary(self.dictionary)
            print(f"Translation '{translation}' deleted successfully!")
        else:
            print("Word or translation not found in dictionary.")

    def translate_word_to_russian(self, word):
        return self.dictionary.get(word, ["Translation not found"])

    def translate_word_to_korean(self, word):
        translations = []
        for korean_word, russian_words in self.dictionary.items():
            if word in russian_words:
                translations.append(korean_word)
        if translations:
            return translations
        else:
            return ["Translation not found"]

    def translate_sentence_to_russian(self, sentence):
        words = re.findall(r'\w+', sentence)
        translated_sentence = []
        for word in words:
            translations = self.translate_word_to_russian(word)
            translated_sentence.extend(translations)

        return ' '.join(translated_sentence)

    def translate_sentence_to_korean(self, sentence):
        words = sentence.split()
        translated_sentence = []
        for word in words:
            translations = self.translate_word_to_korean(word)
            translated_sentence.extend(translations)
        return ' '.join(translated_sentence)

    def print_all_words(self):
        for word, translations in self.dictionary.items():
            print(f"{word}: {', '.join(translations)}")

    def clear_dictionary(self):
        self.dictionary = {}
        self.dictionary_file.save_dictionary(self.dictionary)
        print("Dictionary cleared successfully.")

    def word_exists(self, word):
        return word in self.dictionary.keys()

    def add_translation_to_history(self, translation):
        self.translation_history.append(translation)

    def print_translation_history(self):
        for translation in self.translation_history:
            print(translation)

    def save_translation_history(self):
        with open("translation_history.txt", "w") as file:
            for translation in self.translation_history:
                file.write(translation + "\n")


def main():
    dictionary_file = "dictionary.csv"
    translator = Translator(dictionary_file)

    while True:
        print("-------------------------------------")
        print("Enter one of the following operations:")
        print("'kr' - translate from Korean to Russian")
        print("'rk' - translate from Russian to Korean")
        print("'m' - addition options")
        print("'q' - quit")
        print("-------------------------------------")

        choice = input("Your choice: ")

        if choice.lower() == "q":
            translator.save_translation_history()
            break

        if choice.lower() == "kr":
            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'W' - translate a word")
            print("'S' - translate a sentence")
            print("'B' - go back to the main menu")
            print("-------------------------------------")

            choice_2 = input("Your choice: ")

            if choice_2.lower() == "w":
                word = input("Enter a word to translate from Korean to Russian: ")
                translations = translator.translate_word_to_russian(word)
                print(f"Translation: {', '.join(translations)}")
                translator.add_translation_to_history(f"{word}: {', '.join(translations)}")

            elif choice_2.lower() == "s":
                sentence = input("Enter a sentence to translate from Korean to Russian: ")
                translation = translator.translate_sentence_to_russian(sentence)
                print(f"Sentence translation: {translation}")
                translator.add_translation_to_history(f"{sentence}: {translation}")

            elif choice_2.lower() == "b":
                continue
        
        if choice.lower() == "rk":
            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'W' - translate a word")
            print("'S' - translate a sentence")
            print("'B' - go back to the main menu")
            print("-------------------------------------")

            choice_2 = input("Your choice: ")

            if choice_2.lower() == "w":
                word = input("Enter a word to translate from Russian to Korean: ")
                translations = translator.translate_word_to_korean(word)
                print(f"Translation: {', '.join(translations)}")

                translator.add_translation_to_history(f"{word}: {', '.join(translations)}")

            elif choice_2.lower() == "s":
                sentence = input("Enter a sentence to translate from Russian to Korean: ")
                translation = translator.translate_sentence_to_korean(sentence)
                print(f"Sentence translation: {translation}")
                translator.add_translation_to_history(f"{sentence}: {translation}")
            
            elif choice_2.lower() == "b":
                continue

        if choice.lower() == "m":
            print("-------------------------------------")
            print("Enter one of the following operations:")
            print("'a' - add a word")
            print("'d' - delete a translation")
            print("'u' - update a translation")
            print("'c' - clear the dictionary")
            print("'p' - print all words in the dictionary")
            print("'s' - select another dictionary file")
            print("'e' - export dictionary to Excel")
            print("'h' - print translation history")
            print("'b' - go back to the main menu")
            print("-------------------------------------")

            choice_2 = input("Your choice: ")

            if choice_2.lower() == "a":
                word = input("Enter a word to add: ")
                translations = []
                while True:
                    translation = input("Enter a translation (or Enter to finish): ")
                    if not translation:
                        break
                    translations.append(translation)
                if translations:
                    translator.update_dictionary(word, translations)
                    print("Word added to the dictionary successfully!")
                else:
                    print("Nothing added to the dictionary.")

            elif choice_2.lower() == "d":
                word = input("Enter a word to delete translations: ")
                translation = input("Enter a translation to delete: ")
                translator.delete_translation(word, translation)

            elif choice_2.lower() == "u":
                word = input("Enter a word to update translations: ")
                old_translation = input("Enter the old translation: ")
                new_translation = input("Enter the new translation: ")
                if translator.word_exists(word) and old_translation in translator.translate_word_to_russian(word):
                    translator.delete_translation(word, old_translation)
                    translator.update_dictionary(word, [new_translation])
                    print("Translation updated successfully!")
                else:
                    print("Word or translation not found in dictionary.")

            elif choice_2.lower() == "c":
                translator.clear_dictionary()

            elif choice_2.lower() == "p":
                translator.print_all_words()

            elif choice_2.lower() == "s":
                dictionary_file = input("Enter the path to the dictionary file: ")
                translator = Translator(dictionary_file)

            elif choice_2.lower() == "e":
                translator.dictionary_file.export_dictionary_to_excel(translator.dictionary)

            elif choice_2.lower() == "h":
                translator.print_translation_history()
            
            elif choice_2.lower() == "b":
                continue


if __name__ == "__main__":
    main()
