import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';


import '../../core/theme.dart';
import '../../data/local/database.dart';
import '../../domain/geo.dart';
import '../../providers.dart';
import '../../widgets/common.dart';

class ParcelDetailScreen extends ConsumerWidget {
  const ParcelDetailScreen({super.key, required this.parcelId});
  final String parcelId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Parcelle')),
      body: FutureBuilder<Parcel?>(
        future: ref.read(parcelDaoProvider).byId(parcelId),
        builder: (context, snap) {
          final p = snap.data;
          if (p == null) {
            return const Center(child: Text('Parcelle introuvable'));
          }
          final ring = Geo.fromGeoJson(p.geojson);
          final center = Geo.centroid(ring);
          return ListView(
            children: [
              SizedBox(
                height: 260,
                child: FlutterMap(
                  options: MapOptions(initialCenter: center, initialZoom: 16),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'ci.cacaosat',
                    ),
                    PolygonLayer(polygons: [
                      Polygon(
                        points: ring,
                        color: CacaoTheme.eudrColor(p.eudrStatus)
                            .withValues(alpha: 0.3),
                        borderColor: CacaoTheme.eudrColor(p.eudrStatus),
                        borderStrokeWidth: 2.5,
                      ),
                    ]),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(p.code,
                            style: const TextStyle(
                                fontSize: 22, fontWeight: FontWeight.w800)),
                        const Spacer(),
                        EudrTag(status: p.eudrStatus),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${p.areaHa.toStringAsFixed(2)} ha · '
                      'relevé le ${DateFormat('dd/MM/yyyy').format(p.collectedAt)} · '
                      '${_stateLabel(p.syncState)}',
                      style: TextStyle(
                          color: CacaoTheme.sand.withValues(alpha: 0.6)),
                    ),
                    const SizedBox(height: 16),
                    if (p.score != null)
                      SectionCard(
                        child: Row(
                          children: [
                            Text(p.score!.toStringAsFixed(0),
                                style: const TextStyle(
                                    fontSize: 40, fontWeight: FontWeight.w800)),
                            const Text(' / 100'),
                            const Spacer(),
                            Text(CacaoTheme.eudrLabel(p.eudrStatus),
                                style: TextStyle(
                                    color:
                                        CacaoTheme.eudrColor(p.eudrStatus))),
                          ],
                        ),
                      )
                    else
                      SectionCard(
                        child: Text(
                          p.syncState == 'pending'
                              ? 'Score EUDR calculé après synchronisation.'
                              : 'Analyse en cours côté serveur…',
                          style: TextStyle(
                              color: CacaoTheme.sand.withValues(alpha: 0.6)),
                        ),
                      ),
                    const SizedBox(height: 12),
                    _KV('Surface', '${p.areaHa.toStringAsFixed(3)} ha'),
                    _KV('Périmètre',
                        '${Geo.perimeterM(ring).toStringAsFixed(0)} m'),
                    _KV('Sommets', '${ring.length}'),
                    _KV('Précision GPS',
                        p.gpsAccuracyM == null
                            ? '—'
                            : '${p.gpsAccuracyM!.toStringAsFixed(0)} m'),
                    _KV('Méthode', p.collectionMethod),
                    _KV('Année de plantation',
                        p.plantingYear?.toString() ?? '—'),
                    if (p.note != null) _KV('Note', p.note!),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  static String _stateLabel(String s) => switch (s) {
        'pending' => 'à synchroniser',
        'synced' => 'synchronisée',
        'analyzed' => 'analysée',
        _ => s,
      };
}

class _KV extends StatelessWidget {
  const _KV(this.k, this.v);
  final String k;
  final String v;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(k,
                style: TextStyle(
                    color: CacaoTheme.sand.withValues(alpha: 0.55))),
            Text(v, style: const TextStyle(fontWeight: FontWeight.w600)),
          ],
        ),
      );
}
