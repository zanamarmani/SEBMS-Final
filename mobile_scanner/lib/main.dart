import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

import 'reading.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Firebase.initializeApp();
    runApp(const ScannerApp());
  } catch (_) {
    runApp(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: Text(
              'Firebase setup required. Follow mobile_scanner/README.md.',
            ),
          ),
        ),
      ),
    );
  }
}

class ScannerApp extends StatelessWidget {
  const ScannerApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'SEBMS Meter Scanner',
    theme: ThemeData(
      useMaterial3: true,
      colorSchemeSeed: const Color(0xff2563eb),
      scaffoldBackgroundColor: const Color(0xfff8fafc),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(),
      ),
    ),
    home: StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        return snapshot.data == null ? const LoginPage() : const ScanPage();
      },
    ),
  );
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController(), password = TextEditingController();
  bool busy = false;
  String? error;
  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> login() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: email.text.trim(),
        password: password.text,
      );
    } on FirebaseAuthException {
      if (mounted)
        setState(
          () => error =
              'Sign-in failed. Check your reader account and connection.',
        );
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(
                Icons.electric_meter,
                size: 64,
                color: Color(0xff2563eb),
              ),
              const SizedBox(height: 20),
              const Text(
                'SEBMS',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
              const Text(
                'Field meter readings',
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 28),
              TextField(
                controller: email,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'Reader email'),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: password,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Password'),
              ),
              if (error != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Text(
                    error!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: busy ? null : login,
                child: Text(busy ? 'Signing in…' : 'Sign in'),
              ),
              const SizedBox(height: 12),
              const Text(
                'Use your Firebase reader account. Django credentials are separate.',
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class ScanPage extends StatefulWidget {
  const ScanPage({super.key});
  @override
  State<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends State<ScanPage> {
  final serial = TextEditingController(), value = TextEditingController();
  final form = GlobalKey<FormState>();
  final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
  DateTime date = DateTime.now();
  XFile? photo;
  List<String> candidates = [];
  bool busy = false, confirmed = false;
  String status = 'Capture a clear photo of the meter label and display.';
  @override
  void dispose() {
    serial.dispose();
    value.dispose();
    recognizer.close();
    super.dispose();
  }

  Future<void> capture() async {
    setState(() {
      busy = true;
      confirmed = false;
    });
    try {
      final image = await ImagePicker().pickImage(
        source: ImageSource.camera,
        imageQuality: 90,
        maxWidth: 2400,
      );
      if (image == null) return;
      final text = await recognizer.processImage(
        InputImage.fromFilePath(image.path),
      );
      final numbers = RegExp(r'\b\d+(?:\.\d+)?\b')
          .allMatches(text.text)
          .map((m) => m.group(0)!)
          .toSet()
          .toList();
      if (mounted)
        setState(() {
          photo = image;
          candidates = numbers;
          status = 'Tap a detected number, choose its field, then verify against the photo.';
        });
    } catch (_) {
      if (mounted)
        setState(
          () => status = 'Camera or recognition failed. Allow camera access, retry, or enter the values manually.',
        );
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> send() async {
    if (!form.currentState!.validate() || !confirmed) return;
    setState(() => busy = true);
    try {
      final data = Reading(
        serial.text.trim(),
        value.text.trim(),
        date,
      ).toJson();
      // Existing Django importer reads exactly this document and array.
      // arrayUnion is atomic and exact-payload retries do not duplicate entries.
      await FirebaseFirestore.instance
          .collection('meters')
          .doc('your_doc_id')
          .set({
            'meter_list': FieldValue.arrayUnion([data]),
          }, SetOptions(merge: true));
      if (mounted)
        setState(() {
          status = 'Reading synced to Firebase. Use Fetch readings in SEBMS to import it.';
          confirmed = false;
          serial.clear();
          value.clear();
          photo = null;
          candidates = [];
        });
    } catch (_) {
      if (mounted)
        setState(
          () => status = 'Sync not confirmed. Check connectivity and reader permissions; your values remain here for retry.',
        );
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('SEBMS • Meter reader'),
      actions: [
        IconButton(
          tooltip: 'Sign out',
          onPressed: busy ? null : () => FirebaseAuth.instance.signOut(),
          icon: const Icon(Icons.logout),
        ),
      ],
    ),
    body: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 600),
        child: Form(
          key: form,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              const Text(
                'Capture a reading',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const Text(
                'SCAN  →  VERIFY  →  SYNC',
                style: TextStyle(color: Color(0xff64748b)),
              ),
              const SizedBox(height: 20),
              if (photo != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.file(
                    File(photo!.path),
                    height: 220,
                    fit: BoxFit.contain,
                  ),
                )
              else
                Container(
                  height: 180,
                  decoration: BoxDecoration(
                    color: const Color(0xffdbeafe),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(
                    Icons.document_scanner_outlined,
                    size: 64,
                    color: Color(0xff2563eb),
                  ),
                ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: busy ? null : capture,
                icon: const Icon(Icons.camera_alt_outlined),
                label: Text(photo == null ? 'Scan meter' : 'Retake photo'),
              ),
              if (busy) const LinearProgressIndicator(),
              const SizedBox(height: 16),
              Text(status),
              if (candidates.isNotEmpty)
                Wrap(
                  spacing: 8,
                  children: candidates
                      .map(
                        (number) => ActionChip(
                          label: Text(number),
                          onPressed: busy
                              ? null
                              : () async {
                                  final field = await showDialog<String>(
                                    context: context,
                                    builder: (context) => SimpleDialog(
                                      title: Text('Use $number as'),
                                      children: [
                                        SimpleDialogOption(
                                          onPressed: () =>
                                              Navigator.pop(context, 'serial'),
                                          child: const Text('Meter number'),
                                        ),
                                        SimpleDialogOption(
                                          onPressed: () =>
                                              Navigator.pop(context, 'reading'),
                                          child: const Text('Reading'),
                                        ),
                                      ],
                                    ),
                                  );
                                  if (mounted && field != null)
                                    setState(() {
                                      (field == 'serial' ? serial : value)
                                              .text =
                                          number;
                                      confirmed = false;
                                    });
                                },
                        ),
                      )
                      .toList(),
                ),
              const SizedBox(height: 20),
              TextFormField(
                controller: serial,
                enabled: !busy,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                decoration: const InputDecoration(
                  labelText: 'Meter serial number',
                  helperText: 'Must match an existing SEBMS meter',
                ),
                validator: (v) =>
                    int.tryParse(v ?? '') == null || int.parse(v!) <= 0
                    ? 'Enter a positive meter number'
                    : null,
                onChanged: (_) => setState(() => confirmed = false),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: value,
                enabled: !busy,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                decoration: const InputDecoration(
                  labelText: 'Reading (whole kWh)',
                  helperText:
                      'Verify digits; do not include decimal dial digits',
                ),
                validator: (v) => int.tryParse(v ?? '') == null
                    ? 'Enter a whole reading'
                    : null,
                onChanged: (_) => setState(() => confirmed = false),
              ),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Reading date'),
                subtitle: Text(
                  '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
                ),
                trailing: const Icon(Icons.calendar_month),
                onTap: busy
                    ? null
                    : () async {
                        final chosen = await showDatePicker(
                          context: context,
                          initialDate: date,
                          firstDate: DateTime(2020),
                          lastDate: DateTime.now(),
                        );
                        if (chosen != null && mounted)
                          setState(() {
                            date = chosen;
                            confirmed = false;
                          });
                      },
              ),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                value: confirmed,
                onChanged: busy
                    ? null
                    : (v) => setState(() => confirmed = v ?? false),
                title: const Text(
                  'I verified the meter number, reading and date.',
                ),
              ),
              FilledButton.icon(
                onPressed: busy || !confirmed ? null : send,
                icon: const Icon(Icons.cloud_upload_outlined),
                label: const Text('Send to Firebase'),
              ),
              const SizedBox(height: 12),
              const Text(
                'Firebase sync does not generate a bill. SEBMS imports and processes the reading separately.',
                style: TextStyle(color: Color(0xff64748b)),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
