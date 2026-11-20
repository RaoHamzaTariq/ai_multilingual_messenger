import 'package:audioplayers/audioplayers.dart';
import 'package:cross_file/cross_file.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

class AudioService {
  static final AudioService instance = AudioService._internal();
  AudioService._internal();

  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  AudioPlayer get player => _player;

  Future<bool> hasPermission() async {
    return await _recorder.hasPermission();
  }

  Future<bool> isRecording() async {
    return await _recorder.isRecording();
  }

  Future<bool> startRecording() async {
    try {
      if (kIsWeb) {
        // On web, Chrome and modern browsers require Opus encoder for MediaRecorder
        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.opus,
          ),
          path: '',
        );
      } else {
        if (!await _recorder.hasPermission()) {
          return false;
        }
        final tempDir = await getTemporaryDirectory();
        final path =
            '${tempDir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.m4a';

        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.aacLc,
            bitRate: 128000,
            sampleRate: 44100,
          ),
          path: path,
        );
      }
      return true;
    } catch (e) {
      debugPrint('Error starting audio recording: $e');
      return false;
    }
  }

  Future<Uint8List?> stopRecordingAndGetBytes() async {
    if (!await _recorder.isRecording()) {
      return null;
    }

    try {
      final pathOrUrl = await _recorder.stop();
      if (pathOrUrl == null) return null;

      if (kIsWeb) {
        // On web, pathOrUrl is a blob: URL
        try {
          final res = await http.get(Uri.parse(pathOrUrl));
          if (res.statusCode == 200) {
            return res.bodyBytes;
          }
        } catch (_) {}
        final file = XFile(pathOrUrl);
        return await file.readAsBytes();
      } else {
        final file = XFile(pathOrUrl);
        return await file.readAsBytes();
      }
    } catch (_) {
      return null;
    }
  }

  Future<void> cancelRecording() async {
    if (await _recorder.isRecording()) {
      await _recorder.stop();
    }
  }

  Future<void> playUrl(String url) async {
    await _player.stop();
    await _player.play(UrlSource(url));
  }

  Future<void> pause() async {
    await _player.pause();
  }

  Future<void> resume() async {
    await _player.resume();
  }

  Future<void> stop() async {
    await _player.stop();
  }

  void dispose() {
    _recorder.dispose();
    _player.dispose();
  }
}
