import tempfile
import unittest
from pathlib import Path

from log_service import append_log, read_logs


class LogServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.log_file = self.root / "app.log"

    def tearDown(self):
        self.temp.cleanup()

    def test_u1_first_write_creates_file(self):
        append_log("[INFO] Primeiro.", self.log_file)
        self.assertTrue(self.log_file.exists())
        self.assertEqual(self.log_file.read_text(encoding="utf-8"), "[INFO] Primeiro.\n")

    def test_u2_different_writes_preserve_order(self):
        append_log("[INFO] Um.", self.log_file)
        append_log("[WARNING] Dois.", self.log_file)
        self.assertEqual(read_logs(self.log_file), ["[INFO] Um.", "[WARNING] Dois."])

    def test_u3_duplicate_writes_are_both_kept(self):
        append_log("[INFO] Igual.", self.log_file)
        append_log("[INFO] Igual.", self.log_file)
        self.assertEqual(read_logs(self.log_file), ["[INFO] Igual.", "[INFO] Igual."])

    def test_u4_missing_and_empty_files_return_empty_list(self):
        self.assertEqual(read_logs(self.root / "missing.log"), [])
        self.log_file.touch()
        self.assertEqual(read_logs(self.log_file), [])

    def test_u5_utf8_punctuation_and_accents_round_trip(self):
        entry = '[INFO] Ação concluída, "ótimo".'
        append_log(entry, self.log_file)
        self.assertEqual(read_logs(self.log_file), [entry])

    def test_u6_data_survives_reopening_file(self):
        append_log("[ERROR] Falha fictícia.", self.log_file)
        # read_logs abre o arquivo novamente, sem depender de estado em memória.
        self.assertEqual(read_logs(self.log_file), ["[ERROR] Falha fictícia."])

    def test_u7_invalid_write_destination_raises_oserror(self):
        with self.assertRaises(OSError):
            append_log("[INFO] Não gravar.", self.root)

    def test_u8_unreadable_source_directory_raises_oserror(self):
        with self.assertRaises(OSError):
            read_logs(self.root)


if __name__ == "__main__":
    unittest.main()
