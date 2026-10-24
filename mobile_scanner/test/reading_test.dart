import 'package:flutter_test/flutter_test.dart';
import 'package:sebms_scanner/reading.dart';

void main() {
  test('uses the exact Django ingestion contract', () {
    expect(Reading('12345', '5678', DateTime(2026, 10, 24)).toJson(),
      {'serial_no': 12345, 'reading': 5678, 'date': '2026-10-24'});
  });
  test('rejects malformed serials and decimal readings', () {
    expect(() => Reading('ABC', '1', DateTime.now()).toJson(), throwsFormatException);
    expect(() => Reading('1', '3.5', DateTime.now()).toJson(), throwsFormatException);
    expect(() => Reading('0', '3', DateTime.now()).toJson(), throwsFormatException);
  });
}
