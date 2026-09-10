import 'dart:async';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/foundation.dart';
import 'package:flutter/painting.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

/// Instance partagée réutilisable pour les écrans qui n'ont pas de cycle de vie
/// propre (widgets sans état).
final sharedTileProvider = CachedTileProvider();

/// Fournisseur de tuiles avec cache disque : une zone déjà consultée reste
/// affichable hors-ligne. Cache borné (~40 Mo) avec éviction LRU grossière.
class CachedTileProvider extends TileProvider {
  CachedTileProvider();

  Directory? _dir;
  final _client = http.Client();
  static const _maxBytes = 40 * 1024 * 1024;

  Future<Directory> _cacheDir() async {
    if (_dir != null) return _dir!;
    final base = await getApplicationSupportDirectory();
    final d = Directory(p.join(base.path, 'tile_cache'));
    if (!d.existsSync()) d.createSync(recursive: true);
    _dir = d;
    return d;
  }

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    final url = getTileUrl(coordinates, options);
    return _CachedNetworkImage(url, _cacheDir, _client);
  }

  Future<void> pruneIfNeeded() async {
    final d = await _cacheDir();
    final files = d.listSync().whereType<File>().toList()
      ..sort((a, b) => a.statSync().modified.compareTo(b.statSync().modified));
    var total = files.fold<int>(0, (s, f) => s + f.lengthSync());
    for (final f in files) {
      if (total <= _maxBytes) break;
      total -= f.lengthSync();
      f.deleteSync();
    }
  }

  @override
  void dispose() {
    _client.close();
    super.dispose();
  }
}

class _CachedNetworkImage extends ImageProvider<_CachedNetworkImage> {
  _CachedNetworkImage(this.url, this._dir, this._client);
  final String url;
  final Future<Directory> Function() _dir;
  final http.Client _client;

  String get _key => url.hashCode.toRadixString(16);

  @override
  Future<_CachedNetworkImage> obtainKey(ImageConfiguration configuration) =>
      SynchronousFuture(this);

  @override
  ImageStreamCompleter loadImage(_CachedNetworkImage key, ImageDecoderCallback decode) {
    return MultiFrameImageStreamCompleter(
      codec: _load(decode),
      scale: 1.0,
      debugLabel: url,
    );
  }

  Future<ui.Codec> _load(ImageDecoderCallback decode) async {
    final dir = await _dir();
    final file = File(p.join(dir.path, _key));
    Uint8List bytes;
    if (file.existsSync()) {
      bytes = await file.readAsBytes();
      file.setLastModifiedSync(DateTime.now());
    } else {
      final res = await _client.get(Uri.parse(url), headers: {
        'User-Agent': 'ci.cacaosat (offline tile cache)',
      });
      if (res.statusCode != 200) {
        throw NetworkImageLoadException(statusCode: res.statusCode, uri: Uri.parse(url));
      }
      bytes = res.bodyBytes;
      unawaited(file.writeAsBytes(bytes));
    }
    return decode(await ui.ImmutableBuffer.fromUint8List(bytes));
  }

  @override
  bool operator ==(Object other) => other is _CachedNetworkImage && other.url == url;

  @override
  int get hashCode => url.hashCode;
}
