import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../core/nav.dart';
import '../../core/theme.dart';
import '../../core/tile_cache.dart';
import '../../domain/geo.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

enum CaptureMode { walk, vertices, manual }

class CaptureScreen extends ConsumerStatefulWidget {
  const CaptureScreen({super.key});

  @override
  ConsumerState<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends ConsumerState<CaptureScreen> {
  final _map = MapController();
  final _tiles = CachedTileProvider();
  final List<LatLng> _points = [];
  final List<List<LatLng>> _protectedRings = [];

  CaptureMode _mode = CaptureMode.vertices;
  StreamSubscription<Position>? _posSub;
  Position? _current;
  bool _walking = false;
  bool _saving = false;
  Timer? _draftTimer;

  @override
  void initState() {
    super.initState();
    _initLocation();
    _loadProtected();
    _offerDraftResume();
  }

  @override
  void dispose() {
    _posSub?.cancel();
    _draftTimer?.cancel();
    _tiles.dispose();
    super.dispose();
  }

  Future<void> _offerDraftResume() async {
    final draft = await ref.read(referenceRepositoryProvider).loadDraft();
    if (draft == null || !mounted) return;
    final resume = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Reprendre la capture ?'),
        content: Text('Un relevé de ${draft.points.length} sommets a été interrompu.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Recommencer'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Reprendre'),
          ),
        ],
      ),
    );
    if (resume == true && mounted) {
      setState(() {
        _points
          ..clear()
          ..addAll(draft.points.map((c) => LatLng(c[0], c[1])));
        _mode = CaptureMode.values.firstWhere(
          (m) => m.name == draft.mode,
          orElse: () => CaptureMode.vertices,
        );
      });
      if (_points.isNotEmpty) _map.move(_points.first, 17);
    } else {
      await ref.read(referenceRepositoryProvider).clearDraft();
    }
  }

  void _persistDraft() {
    _draftTimer?.cancel();
    _draftTimer = Timer(const Duration(milliseconds: 600), () {
      ref.read(referenceRepositoryProvider).saveDraft(
            _points.map((p) => [p.latitude, p.longitude]).toList(),
            _mode.name,
          );
    });
  }

  /// setState + sauvegarde différée du brouillon.
  void _editPoints(VoidCallback mutate) {
    setState(mutate);
    _persistDraft();
  }

  Future<void> _loadProtected() async {
    final rings = await ref.read(referenceRepositoryProvider).protectedRings();
    setState(() {
      _protectedRings
        ..clear()
        ..addAll(rings
            .map((r) => r.map((c) => LatLng(c[1], c[0])).toList()));
    });
  }

  Future<void> _initLocation() async {
    try {
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.denied ||
          perm == LocationPermission.deniedForever) {
        return;
      }
    } catch (_) {
      return; // plateforme sans GPS (test / émulateur) : capture manuelle possible
    }
    try {
      final pos = await Geolocator.getCurrentPosition();
      if (!mounted) return;
      setState(() => _current = pos);
      _map.move(LatLng(pos.latitude, pos.longitude), 17);
    } catch (_) {}
    try {
      _posSub = _positionStream();
    } catch (_) {
      // pas de flux GPS : les modes « sommets » (GPS ponctuel) et « manuel » restent utilisables
    }
  }

  StreamSubscription<Position> _positionStream() {
    return Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 3,
      ),
    ).listen((pos) {
      if (!mounted) return;
      setState(() => _current = pos);
      if (_walking && _mode == CaptureMode.walk) {
        final ll = LatLng(pos.latitude, pos.longitude);
        if (_points.isEmpty ||
            const Distance().as(LengthUnit.Meter, _points.last, ll) > 4) {
          _editPoints(() => _points.add(ll));
        }
      }
    });
  }

  double get _areaHa => _points.length >= 3 ? Geo.areaHa(_points) : 0;
  bool get _recoupeAireProtegee =>
      _points.length >= 3 &&
      Geo.intersectsAnyProtected(_points, _protectedRings);

  void _addVertexAtGps() {
    final p = _current;
    if (p == null) return;
    _editPoints(() => _points.add(LatLng(p.latitude, p.longitude)));
  }

  Future<void> _finish() async {
    if (_points.length < 3) {
      _snack('Au moins 3 sommets sont nécessaires.');
      return;
    }
    final repo = ref.read(parcelRepositoryProvider);
    final v = await repo.validate(_points);
    if (!mounted) return;
    if (!v.ok) {
      _snack(v.errors.join('\n'));
      return;
    }
    setState(() => _saving = true);
    final saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _CaptureForm(
        points: List.of(_points),
        areaHa: _areaHa,
        gpsAccuracy: _current?.accuracy,
        warnings: v.warnings,
      ),
    );
    if (!mounted) return;
    setState(() => _saving = false);
    if (saved == true) {
      await ref.read(referenceRepositoryProvider).clearDraft();
      unawaited(_tiles.pruneIfNeeded());
      if (mounted) safePop(context);
    }
  }

  void _snack(String m) => ScaffoldMessenger.of(context)
      .showSnackBar(SnackBar(content: Text(m)));

  @override
  Widget build(BuildContext context) {
    final center = _current != null
        ? LatLng(_current!.latitude, _current!.longitude)
        : const LatLng(6.544, -7.492);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Capturer une parcelle'),
        actions: [
          TextButton(
            onPressed: _points.isEmpty
                ? null
                : () => _editPoints(_points.clear),
            child: const Text('Effacer'),
          ),
        ],
      ),
      body: Column(
        children: [
          const OfflineBanner(),
          _ModeBar(mode: _mode, onChange: (m) => setState(() => _mode = m)),
          Expanded(
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _map,
                  options: MapOptions(
                    initialCenter: center,
                    initialZoom: 17,
                    onTap: _mode == CaptureMode.manual
                        ? (_, ll) => _editPoints(() => _points.add(ll))
                        : null,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'ci.cacaosat',
                      maxZoom: 19,
                      tileProvider: _tiles,
                    ),
                    if (_protectedRings.isNotEmpty)
                      PolygonLayer(
                        polygons: _protectedRings
                            .map((r) => Polygon(
                                  points: r,
                                  color: CacaoTheme.riskHigh
                                      .withValues(alpha: 0.12),
                                  borderColor: CacaoTheme.riskHigh
                                      .withValues(alpha: 0.5),
                                  borderStrokeWidth: 1,
                                ))
                            .toList(),
                      ),
                    if (_points.length >= 2)
                      PolygonLayer(polygons: [
                        Polygon(
                          points: _points,
                          color: (_recoupeAireProtegee
                                  ? CacaoTheme.riskHigh
                                  : CacaoTheme.green)
                              .withValues(alpha: 0.25),
                          borderColor: _recoupeAireProtegee
                              ? CacaoTheme.riskHigh
                              : CacaoTheme.green,
                          borderStrokeWidth: 2.5,
                        ),
                      ]),
                    MarkerLayer(
                      markers: [
                        for (var i = 0; i < _points.length; i++)
                          Marker(
                            point: _points[i],
                            width: 26,
                            height: 26,
                            child: GestureDetector(
                              onTap: _mode == CaptureMode.manual
                                  ? () => _editPoints(() => _points.removeAt(i))
                                  : null,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: CacaoTheme.orange,
                                  shape: BoxShape.circle,
                                  border: Border.all(color: Colors.white, width: 2),
                                ),
                                child: Center(
                                  child: Text('${i + 1}',
                                      style: const TextStyle(
                                          fontSize: 10, color: Colors.white)),
                                ),
                              ),
                            ),
                          ),
                        if (_current != null)
                          Marker(
                            point:
                                LatLng(_current!.latitude, _current!.longitude),
                            width: 18,
                            height: 18,
                            child: Container(
                              decoration: BoxDecoration(
                                color: Colors.blueAccent,
                                shape: BoxShape.circle,
                                border:
                                    Border.all(color: Colors.white, width: 2),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
                Positioned(
                  left: 12,
                  right: 12,
                  bottom: 12,
                  child: _StatsBar(
                    points: _points.length,
                    areaHa: _areaHa,
                    accuracy: _current?.accuracy,
                    warnProtected: _recoupeAireProtegee,
                  ),
                ),
              ],
            ),
          ),
          _ActionBar(
            mode: _mode,
            walking: _walking,
            pointCount: _points.length,
            saving: _saving,
            onToggleWalk: () => setState(() => _walking = !_walking),
            onAddVertex: _addVertexAtGps,
            onUndo: _points.isEmpty
                ? null
                : () => _editPoints(() => _points.removeLast()),
            onFinish: _finish,
          ),
        ],
      ),
    );
  }
}

class _ModeBar extends StatelessWidget {
  const _ModeBar({required this.mode, required this.onChange});
  final CaptureMode mode;
  final ValueChanged<CaptureMode> onChange;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: SegmentedButton<CaptureMode>(
        segments: const [
          ButtonSegment(value: CaptureMode.walk, label: Text('Marche'), icon: Icon(Icons.directions_walk)),
          ButtonSegment(value: CaptureMode.vertices, label: Text('Sommets'), icon: Icon(Icons.place)),
          ButtonSegment(value: CaptureMode.manual, label: Text('Manuel'), icon: Icon(Icons.touch_app)),
        ],
        selected: {mode},
        onSelectionChanged: (s) => onChange(s.first),
      ),
    );
  }
}

class _StatsBar extends StatelessWidget {
  const _StatsBar({
    required this.points,
    required this.areaHa,
    required this.accuracy,
    required this.warnProtected,
  });
  final int points;
  final double areaHa;
  final double? accuracy;
  final bool warnProtected;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: CacaoTheme.night2.withValues(alpha: 0.95),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _Stat(label: 'Sommets', value: '$points'),
                _Stat(label: 'Surface', value: '${areaHa.toStringAsFixed(2)} ha'),
                _Stat(
                  label: 'Précision GPS',
                  value: accuracy == null ? '—' : '${accuracy!.toStringAsFixed(0)} m',
                ),
              ],
            ),
            if (warnProtected) ...[
              const SizedBox(height: 6),
              const Row(children: [
                Icon(Icons.warning_amber, size: 15, color: CacaoTheme.riskHigh),
                SizedBox(width: 6),
                Expanded(
                  child: Text('Recoupe une aire protégée / forêt classée',
                      style: TextStyle(fontSize: 12, color: CacaoTheme.riskHigh)),
                ),
              ]),
            ],
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value,
              style: const TextStyle(
                  fontWeight: FontWeight.w700, color: Colors.white)),
          Text(label,
              style: TextStyle(
                  fontSize: 11, color: CacaoTheme.sand.withValues(alpha: 0.5))),
        ],
      );
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.mode,
    required this.walking,
    required this.pointCount,
    required this.saving,
    required this.onToggleWalk,
    required this.onAddVertex,
    required this.onUndo,
    required this.onFinish,
  });
  final CaptureMode mode;
  final bool walking;
  final int pointCount;
  final bool saving;
  final VoidCallback onToggleWalk;
  final VoidCallback onAddVertex;
  final VoidCallback? onUndo;
  final VoidCallback onFinish;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            IconButton.filledTonal(
              onPressed: onUndo,
              icon: const Icon(Icons.undo),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: switch (mode) {
                CaptureMode.walk => FilledButton.icon(
                    onPressed: onToggleWalk,
                    icon: Icon(walking ? Icons.pause : Icons.play_arrow),
                    label: Text(walking ? 'Pause' : 'Démarrer la marche'),
                  ),
                CaptureMode.vertices => FilledButton.icon(
                    onPressed: onAddVertex,
                    icon: const Icon(Icons.add_location_alt),
                    label: const Text('Ajouter un sommet'),
                  ),
                CaptureMode.manual => const Center(
                    child: Text('Tapez sur la carte pour poser des sommets'),
                  ),
              },
            ),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: (pointCount >= 3 && !saving) ? onFinish : null,
              child: const Text('Terminer'),
            ),
          ],
        ),
      ),
    );
  }
}

class _CaptureForm extends ConsumerStatefulWidget {
  const _CaptureForm({
    required this.points,
    required this.areaHa,
    required this.gpsAccuracy,
    required this.warnings,
  });
  final List<LatLng> points;
  final double areaHa;
  final double? gpsAccuracy;
  final List<String> warnings;

  @override
  ConsumerState<_CaptureForm> createState() => _CaptureFormState();
}

class _CaptureFormState extends ConsumerState<_CaptureForm> {
  String? _producerId;
  final _year = TextEditingController();
  final _note = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _year.dispose();
    _note.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final boot = await ref.read(referenceRepositoryProvider).cachedBootstrap();
    final coop = boot?['cooperative'] as Map<String, dynamic>?;
    await ref.read(parcelRepositoryProvider).create(
          coopId: coop?['id'] as String? ?? 'local',
          coopCode: coop?['code'] as String? ?? 'PARC',
          ring: widget.points,
          producerLocalId: _producerId,
          plantingYear: int.tryParse(_year.text),
          gpsAccuracyM: widget.gpsAccuracy,
          collectionMethod: 'walk',
          note: _note.text.trim().isEmpty ? null : _note.text.trim(),
        );
    if (mounted) Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final producers = ref.watch(producersStreamProvider).valueOrNull ?? [];
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Nouvelle parcelle — ${widget.areaHa.toStringAsFixed(2)} ha',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          for (final w in widget.warnings)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text('⚠ $w',
                  style: const TextStyle(color: CacaoTheme.riskHigh, fontSize: 12)),
            ),
          const SizedBox(height: 14),
          DropdownButtonFormField<String>(
            initialValue: _producerId,
            decoration: const InputDecoration(labelText: 'Producteur'),
            items: [
              const DropdownMenuItem(value: null, child: Text('— non rattaché —')),
              ...producers.map((p) =>
                  DropdownMenuItem(value: p.id, child: Text(p.fullName))),
            ],
            onChanged: (v) => setState(() => _producerId = v),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _year,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Année de plantation'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _note,
            decoration: const InputDecoration(labelText: 'Note (facultatif)'),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: _saving ? null : _save,
              child: Text(_saving ? 'Enregistrement…' : 'Enregistrer la parcelle'),
            ),
          ),
        ],
      ),
    );
  }
}
