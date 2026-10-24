class Reading {
  final String serial;
  final String value;
  final DateTime date;
  Reading(this.serial, this.value, this.date);
  Map<String, dynamic> toJson() {
    if (!RegExp(r'^\d+$').hasMatch(serial) || int.parse(serial) <= 0) {
      throw const FormatException('Enter a positive numeric meter number');
    }
    if (!RegExp(r'^\d+$').hasMatch(value)) {
      throw const FormatException('Enter a whole non-negative reading');
    }
    final day = '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    return {'serial_no': int.parse(serial), 'reading': int.parse(value), 'date': day};
  }
}
