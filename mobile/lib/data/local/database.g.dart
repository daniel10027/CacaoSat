// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'database.dart';

// ignore_for_file: type=lint
class $ProducersTable extends Producers
    with TableInfo<$ProducersTable, Producer> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ProducersTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _serverIdMeta =
      const VerificationMeta('serverId');
  @override
  late final GeneratedColumn<String> serverId = GeneratedColumn<String>(
      'server_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _coopIdMeta = const VerificationMeta('coopId');
  @override
  late final GeneratedColumn<String> coopId = GeneratedColumn<String>(
      'coop_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _fullNameMeta =
      const VerificationMeta('fullName');
  @override
  late final GeneratedColumn<String> fullName = GeneratedColumn<String>(
      'full_name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _nationalIdMeta =
      const VerificationMeta('nationalId');
  @override
  late final GeneratedColumn<String> nationalId = GeneratedColumn<String>(
      'national_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _genderMeta = const VerificationMeta('gender');
  @override
  late final GeneratedColumn<String> gender = GeneratedColumn<String>(
      'gender', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('unknown'));
  static const VerificationMeta _villageMeta =
      const VerificationMeta('village');
  @override
  late final GeneratedColumn<String> village = GeneratedColumn<String>(
      'village', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _phoneMeta = const VerificationMeta('phone');
  @override
  late final GeneratedColumn<String> phone = GeneratedColumn<String>(
      'phone', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _registeredAtMeta =
      const VerificationMeta('registeredAt');
  @override
  late final GeneratedColumn<DateTime> registeredAt = GeneratedColumn<DateTime>(
      'registered_at', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _dirtyMeta = const VerificationMeta('dirty');
  @override
  late final GeneratedColumn<bool> dirty = GeneratedColumn<bool>(
      'dirty', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("dirty" IN (0, 1))'),
      defaultValue: const Constant(true));
  static const VerificationMeta _deletedMeta =
      const VerificationMeta('deleted');
  @override
  late final GeneratedColumn<bool> deleted = GeneratedColumn<bool>(
      'deleted', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("deleted" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        serverId,
        coopId,
        fullName,
        nationalId,
        gender,
        village,
        phone,
        registeredAt,
        dirty,
        deleted,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'producers';
  @override
  VerificationContext validateIntegrity(Insertable<Producer> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('server_id')) {
      context.handle(_serverIdMeta,
          serverId.isAcceptableOrUnknown(data['server_id']!, _serverIdMeta));
    }
    if (data.containsKey('coop_id')) {
      context.handle(_coopIdMeta,
          coopId.isAcceptableOrUnknown(data['coop_id']!, _coopIdMeta));
    } else if (isInserting) {
      context.missing(_coopIdMeta);
    }
    if (data.containsKey('full_name')) {
      context.handle(_fullNameMeta,
          fullName.isAcceptableOrUnknown(data['full_name']!, _fullNameMeta));
    } else if (isInserting) {
      context.missing(_fullNameMeta);
    }
    if (data.containsKey('national_id')) {
      context.handle(
          _nationalIdMeta,
          nationalId.isAcceptableOrUnknown(
              data['national_id']!, _nationalIdMeta));
    }
    if (data.containsKey('gender')) {
      context.handle(_genderMeta,
          gender.isAcceptableOrUnknown(data['gender']!, _genderMeta));
    }
    if (data.containsKey('village')) {
      context.handle(_villageMeta,
          village.isAcceptableOrUnknown(data['village']!, _villageMeta));
    }
    if (data.containsKey('phone')) {
      context.handle(
          _phoneMeta, phone.isAcceptableOrUnknown(data['phone']!, _phoneMeta));
    }
    if (data.containsKey('registered_at')) {
      context.handle(
          _registeredAtMeta,
          registeredAt.isAcceptableOrUnknown(
              data['registered_at']!, _registeredAtMeta));
    }
    if (data.containsKey('dirty')) {
      context.handle(
          _dirtyMeta, dirty.isAcceptableOrUnknown(data['dirty']!, _dirtyMeta));
    }
    if (data.containsKey('deleted')) {
      context.handle(_deletedMeta,
          deleted.isAcceptableOrUnknown(data['deleted']!, _deletedMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Producer map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Producer(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      serverId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}server_id']),
      coopId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}coop_id'])!,
      fullName: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}full_name'])!,
      nationalId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}national_id']),
      gender: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}gender'])!,
      village: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}village']),
      phone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}phone']),
      registeredAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}registered_at']),
      dirty: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}dirty'])!,
      deleted: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}deleted'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $ProducersTable createAlias(String alias) {
    return $ProducersTable(attachedDatabase, alias);
  }
}

class Producer extends DataClass implements Insertable<Producer> {
  final String id;
  final String? serverId;
  final String coopId;
  final String fullName;
  final String? nationalId;
  final String gender;
  final String? village;
  final String? phone;
  final DateTime? registeredAt;
  final bool dirty;
  final bool deleted;
  final DateTime updatedAt;
  const Producer(
      {required this.id,
      this.serverId,
      required this.coopId,
      required this.fullName,
      this.nationalId,
      required this.gender,
      this.village,
      this.phone,
      this.registeredAt,
      required this.dirty,
      required this.deleted,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    if (!nullToAbsent || serverId != null) {
      map['server_id'] = Variable<String>(serverId);
    }
    map['coop_id'] = Variable<String>(coopId);
    map['full_name'] = Variable<String>(fullName);
    if (!nullToAbsent || nationalId != null) {
      map['national_id'] = Variable<String>(nationalId);
    }
    map['gender'] = Variable<String>(gender);
    if (!nullToAbsent || village != null) {
      map['village'] = Variable<String>(village);
    }
    if (!nullToAbsent || phone != null) {
      map['phone'] = Variable<String>(phone);
    }
    if (!nullToAbsent || registeredAt != null) {
      map['registered_at'] = Variable<DateTime>(registeredAt);
    }
    map['dirty'] = Variable<bool>(dirty);
    map['deleted'] = Variable<bool>(deleted);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  ProducersCompanion toCompanion(bool nullToAbsent) {
    return ProducersCompanion(
      id: Value(id),
      serverId: serverId == null && nullToAbsent
          ? const Value.absent()
          : Value(serverId),
      coopId: Value(coopId),
      fullName: Value(fullName),
      nationalId: nationalId == null && nullToAbsent
          ? const Value.absent()
          : Value(nationalId),
      gender: Value(gender),
      village: village == null && nullToAbsent
          ? const Value.absent()
          : Value(village),
      phone:
          phone == null && nullToAbsent ? const Value.absent() : Value(phone),
      registeredAt: registeredAt == null && nullToAbsent
          ? const Value.absent()
          : Value(registeredAt),
      dirty: Value(dirty),
      deleted: Value(deleted),
      updatedAt: Value(updatedAt),
    );
  }

  factory Producer.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Producer(
      id: serializer.fromJson<String>(json['id']),
      serverId: serializer.fromJson<String?>(json['serverId']),
      coopId: serializer.fromJson<String>(json['coopId']),
      fullName: serializer.fromJson<String>(json['fullName']),
      nationalId: serializer.fromJson<String?>(json['nationalId']),
      gender: serializer.fromJson<String>(json['gender']),
      village: serializer.fromJson<String?>(json['village']),
      phone: serializer.fromJson<String?>(json['phone']),
      registeredAt: serializer.fromJson<DateTime?>(json['registeredAt']),
      dirty: serializer.fromJson<bool>(json['dirty']),
      deleted: serializer.fromJson<bool>(json['deleted']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'serverId': serializer.toJson<String?>(serverId),
      'coopId': serializer.toJson<String>(coopId),
      'fullName': serializer.toJson<String>(fullName),
      'nationalId': serializer.toJson<String?>(nationalId),
      'gender': serializer.toJson<String>(gender),
      'village': serializer.toJson<String?>(village),
      'phone': serializer.toJson<String?>(phone),
      'registeredAt': serializer.toJson<DateTime?>(registeredAt),
      'dirty': serializer.toJson<bool>(dirty),
      'deleted': serializer.toJson<bool>(deleted),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  Producer copyWith(
          {String? id,
          Value<String?> serverId = const Value.absent(),
          String? coopId,
          String? fullName,
          Value<String?> nationalId = const Value.absent(),
          String? gender,
          Value<String?> village = const Value.absent(),
          Value<String?> phone = const Value.absent(),
          Value<DateTime?> registeredAt = const Value.absent(),
          bool? dirty,
          bool? deleted,
          DateTime? updatedAt}) =>
      Producer(
        id: id ?? this.id,
        serverId: serverId.present ? serverId.value : this.serverId,
        coopId: coopId ?? this.coopId,
        fullName: fullName ?? this.fullName,
        nationalId: nationalId.present ? nationalId.value : this.nationalId,
        gender: gender ?? this.gender,
        village: village.present ? village.value : this.village,
        phone: phone.present ? phone.value : this.phone,
        registeredAt:
            registeredAt.present ? registeredAt.value : this.registeredAt,
        dirty: dirty ?? this.dirty,
        deleted: deleted ?? this.deleted,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  Producer copyWithCompanion(ProducersCompanion data) {
    return Producer(
      id: data.id.present ? data.id.value : this.id,
      serverId: data.serverId.present ? data.serverId.value : this.serverId,
      coopId: data.coopId.present ? data.coopId.value : this.coopId,
      fullName: data.fullName.present ? data.fullName.value : this.fullName,
      nationalId:
          data.nationalId.present ? data.nationalId.value : this.nationalId,
      gender: data.gender.present ? data.gender.value : this.gender,
      village: data.village.present ? data.village.value : this.village,
      phone: data.phone.present ? data.phone.value : this.phone,
      registeredAt: data.registeredAt.present
          ? data.registeredAt.value
          : this.registeredAt,
      dirty: data.dirty.present ? data.dirty.value : this.dirty,
      deleted: data.deleted.present ? data.deleted.value : this.deleted,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Producer(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('coopId: $coopId, ')
          ..write('fullName: $fullName, ')
          ..write('nationalId: $nationalId, ')
          ..write('gender: $gender, ')
          ..write('village: $village, ')
          ..write('phone: $phone, ')
          ..write('registeredAt: $registeredAt, ')
          ..write('dirty: $dirty, ')
          ..write('deleted: $deleted, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, serverId, coopId, fullName, nationalId,
      gender, village, phone, registeredAt, dirty, deleted, updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Producer &&
          other.id == this.id &&
          other.serverId == this.serverId &&
          other.coopId == this.coopId &&
          other.fullName == this.fullName &&
          other.nationalId == this.nationalId &&
          other.gender == this.gender &&
          other.village == this.village &&
          other.phone == this.phone &&
          other.registeredAt == this.registeredAt &&
          other.dirty == this.dirty &&
          other.deleted == this.deleted &&
          other.updatedAt == this.updatedAt);
}

class ProducersCompanion extends UpdateCompanion<Producer> {
  final Value<String> id;
  final Value<String?> serverId;
  final Value<String> coopId;
  final Value<String> fullName;
  final Value<String?> nationalId;
  final Value<String> gender;
  final Value<String?> village;
  final Value<String?> phone;
  final Value<DateTime?> registeredAt;
  final Value<bool> dirty;
  final Value<bool> deleted;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const ProducersCompanion({
    this.id = const Value.absent(),
    this.serverId = const Value.absent(),
    this.coopId = const Value.absent(),
    this.fullName = const Value.absent(),
    this.nationalId = const Value.absent(),
    this.gender = const Value.absent(),
    this.village = const Value.absent(),
    this.phone = const Value.absent(),
    this.registeredAt = const Value.absent(),
    this.dirty = const Value.absent(),
    this.deleted = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ProducersCompanion.insert({
    required String id,
    this.serverId = const Value.absent(),
    required String coopId,
    required String fullName,
    this.nationalId = const Value.absent(),
    this.gender = const Value.absent(),
    this.village = const Value.absent(),
    this.phone = const Value.absent(),
    this.registeredAt = const Value.absent(),
    this.dirty = const Value.absent(),
    this.deleted = const Value.absent(),
    required DateTime updatedAt,
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        coopId = Value(coopId),
        fullName = Value(fullName),
        updatedAt = Value(updatedAt);
  static Insertable<Producer> custom({
    Expression<String>? id,
    Expression<String>? serverId,
    Expression<String>? coopId,
    Expression<String>? fullName,
    Expression<String>? nationalId,
    Expression<String>? gender,
    Expression<String>? village,
    Expression<String>? phone,
    Expression<DateTime>? registeredAt,
    Expression<bool>? dirty,
    Expression<bool>? deleted,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (serverId != null) 'server_id': serverId,
      if (coopId != null) 'coop_id': coopId,
      if (fullName != null) 'full_name': fullName,
      if (nationalId != null) 'national_id': nationalId,
      if (gender != null) 'gender': gender,
      if (village != null) 'village': village,
      if (phone != null) 'phone': phone,
      if (registeredAt != null) 'registered_at': registeredAt,
      if (dirty != null) 'dirty': dirty,
      if (deleted != null) 'deleted': deleted,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ProducersCompanion copyWith(
      {Value<String>? id,
      Value<String?>? serverId,
      Value<String>? coopId,
      Value<String>? fullName,
      Value<String?>? nationalId,
      Value<String>? gender,
      Value<String?>? village,
      Value<String?>? phone,
      Value<DateTime?>? registeredAt,
      Value<bool>? dirty,
      Value<bool>? deleted,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return ProducersCompanion(
      id: id ?? this.id,
      serverId: serverId ?? this.serverId,
      coopId: coopId ?? this.coopId,
      fullName: fullName ?? this.fullName,
      nationalId: nationalId ?? this.nationalId,
      gender: gender ?? this.gender,
      village: village ?? this.village,
      phone: phone ?? this.phone,
      registeredAt: registeredAt ?? this.registeredAt,
      dirty: dirty ?? this.dirty,
      deleted: deleted ?? this.deleted,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (serverId.present) {
      map['server_id'] = Variable<String>(serverId.value);
    }
    if (coopId.present) {
      map['coop_id'] = Variable<String>(coopId.value);
    }
    if (fullName.present) {
      map['full_name'] = Variable<String>(fullName.value);
    }
    if (nationalId.present) {
      map['national_id'] = Variable<String>(nationalId.value);
    }
    if (gender.present) {
      map['gender'] = Variable<String>(gender.value);
    }
    if (village.present) {
      map['village'] = Variable<String>(village.value);
    }
    if (phone.present) {
      map['phone'] = Variable<String>(phone.value);
    }
    if (registeredAt.present) {
      map['registered_at'] = Variable<DateTime>(registeredAt.value);
    }
    if (dirty.present) {
      map['dirty'] = Variable<bool>(dirty.value);
    }
    if (deleted.present) {
      map['deleted'] = Variable<bool>(deleted.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ProducersCompanion(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('coopId: $coopId, ')
          ..write('fullName: $fullName, ')
          ..write('nationalId: $nationalId, ')
          ..write('gender: $gender, ')
          ..write('village: $village, ')
          ..write('phone: $phone, ')
          ..write('registeredAt: $registeredAt, ')
          ..write('dirty: $dirty, ')
          ..write('deleted: $deleted, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ParcelsTable extends Parcels with TableInfo<$ParcelsTable, Parcel> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ParcelsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _serverIdMeta =
      const VerificationMeta('serverId');
  @override
  late final GeneratedColumn<String> serverId = GeneratedColumn<String>(
      'server_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _producerLocalIdMeta =
      const VerificationMeta('producerLocalId');
  @override
  late final GeneratedColumn<String> producerLocalId = GeneratedColumn<String>(
      'producer_local_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _coopIdMeta = const VerificationMeta('coopId');
  @override
  late final GeneratedColumn<String> coopId = GeneratedColumn<String>(
      'coop_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _codeMeta = const VerificationMeta('code');
  @override
  late final GeneratedColumn<String> code = GeneratedColumn<String>(
      'code', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _geojsonMeta =
      const VerificationMeta('geojson');
  @override
  late final GeneratedColumn<String> geojson = GeneratedColumn<String>(
      'geojson', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _areaHaMeta = const VerificationMeta('areaHa');
  @override
  late final GeneratedColumn<double> areaHa = GeneratedColumn<double>(
      'area_ha', aliasedName, false,
      type: DriftSqlType.double,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _plantingYearMeta =
      const VerificationMeta('plantingYear');
  @override
  late final GeneratedColumn<int> plantingYear = GeneratedColumn<int>(
      'planting_year', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _cropMeta = const VerificationMeta('crop');
  @override
  late final GeneratedColumn<String> crop = GeneratedColumn<String>(
      'crop', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('cocoa'));
  static const VerificationMeta _gpsAccuracyMMeta =
      const VerificationMeta('gpsAccuracyM');
  @override
  late final GeneratedColumn<double> gpsAccuracyM = GeneratedColumn<double>(
      'gps_accuracy_m', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _collectionMethodMeta =
      const VerificationMeta('collectionMethod');
  @override
  late final GeneratedColumn<String> collectionMethod = GeneratedColumn<String>(
      'collection_method', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('walk'));
  static const VerificationMeta _collectedAtMeta =
      const VerificationMeta('collectedAt');
  @override
  late final GeneratedColumn<DateTime> collectedAt = GeneratedColumn<DateTime>(
      'collected_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _noteMeta = const VerificationMeta('note');
  @override
  late final GeneratedColumn<String> note = GeneratedColumn<String>(
      'note', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncStateMeta =
      const VerificationMeta('syncState');
  @override
  late final GeneratedColumn<String> syncState = GeneratedColumn<String>(
      'sync_state', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('pending'));
  static const VerificationMeta _scoreMeta = const VerificationMeta('score');
  @override
  late final GeneratedColumn<double> score = GeneratedColumn<double>(
      'score', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _eudrStatusMeta =
      const VerificationMeta('eudrStatus');
  @override
  late final GeneratedColumn<String> eudrStatus = GeneratedColumn<String>(
      'eudr_status', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        serverId,
        producerLocalId,
        coopId,
        code,
        geojson,
        areaHa,
        plantingYear,
        crop,
        gpsAccuracyM,
        collectionMethod,
        collectedAt,
        note,
        syncState,
        score,
        eudrStatus,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'parcels';
  @override
  VerificationContext validateIntegrity(Insertable<Parcel> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('server_id')) {
      context.handle(_serverIdMeta,
          serverId.isAcceptableOrUnknown(data['server_id']!, _serverIdMeta));
    }
    if (data.containsKey('producer_local_id')) {
      context.handle(
          _producerLocalIdMeta,
          producerLocalId.isAcceptableOrUnknown(
              data['producer_local_id']!, _producerLocalIdMeta));
    }
    if (data.containsKey('coop_id')) {
      context.handle(_coopIdMeta,
          coopId.isAcceptableOrUnknown(data['coop_id']!, _coopIdMeta));
    } else if (isInserting) {
      context.missing(_coopIdMeta);
    }
    if (data.containsKey('code')) {
      context.handle(
          _codeMeta, code.isAcceptableOrUnknown(data['code']!, _codeMeta));
    } else if (isInserting) {
      context.missing(_codeMeta);
    }
    if (data.containsKey('geojson')) {
      context.handle(_geojsonMeta,
          geojson.isAcceptableOrUnknown(data['geojson']!, _geojsonMeta));
    } else if (isInserting) {
      context.missing(_geojsonMeta);
    }
    if (data.containsKey('area_ha')) {
      context.handle(_areaHaMeta,
          areaHa.isAcceptableOrUnknown(data['area_ha']!, _areaHaMeta));
    }
    if (data.containsKey('planting_year')) {
      context.handle(
          _plantingYearMeta,
          plantingYear.isAcceptableOrUnknown(
              data['planting_year']!, _plantingYearMeta));
    }
    if (data.containsKey('crop')) {
      context.handle(
          _cropMeta, crop.isAcceptableOrUnknown(data['crop']!, _cropMeta));
    }
    if (data.containsKey('gps_accuracy_m')) {
      context.handle(
          _gpsAccuracyMMeta,
          gpsAccuracyM.isAcceptableOrUnknown(
              data['gps_accuracy_m']!, _gpsAccuracyMMeta));
    }
    if (data.containsKey('collection_method')) {
      context.handle(
          _collectionMethodMeta,
          collectionMethod.isAcceptableOrUnknown(
              data['collection_method']!, _collectionMethodMeta));
    }
    if (data.containsKey('collected_at')) {
      context.handle(
          _collectedAtMeta,
          collectedAt.isAcceptableOrUnknown(
              data['collected_at']!, _collectedAtMeta));
    } else if (isInserting) {
      context.missing(_collectedAtMeta);
    }
    if (data.containsKey('note')) {
      context.handle(
          _noteMeta, note.isAcceptableOrUnknown(data['note']!, _noteMeta));
    }
    if (data.containsKey('sync_state')) {
      context.handle(_syncStateMeta,
          syncState.isAcceptableOrUnknown(data['sync_state']!, _syncStateMeta));
    }
    if (data.containsKey('score')) {
      context.handle(
          _scoreMeta, score.isAcceptableOrUnknown(data['score']!, _scoreMeta));
    }
    if (data.containsKey('eudr_status')) {
      context.handle(
          _eudrStatusMeta,
          eudrStatus.isAcceptableOrUnknown(
              data['eudr_status']!, _eudrStatusMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Parcel map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Parcel(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      serverId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}server_id']),
      producerLocalId: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}producer_local_id']),
      coopId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}coop_id'])!,
      code: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}code'])!,
      geojson: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}geojson'])!,
      areaHa: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}area_ha'])!,
      plantingYear: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}planting_year']),
      crop: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}crop'])!,
      gpsAccuracyM: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}gps_accuracy_m']),
      collectionMethod: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}collection_method'])!,
      collectedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}collected_at'])!,
      note: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}note']),
      syncState: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}sync_state'])!,
      score: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}score']),
      eudrStatus: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}eudr_status']),
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $ParcelsTable createAlias(String alias) {
    return $ParcelsTable(attachedDatabase, alias);
  }
}

class Parcel extends DataClass implements Insertable<Parcel> {
  final String id;
  final String? serverId;
  final String? producerLocalId;
  final String coopId;
  final String code;
  final String geojson;
  final double areaHa;
  final int? plantingYear;
  final String crop;
  final double? gpsAccuracyM;
  final String collectionMethod;
  final DateTime collectedAt;
  final String? note;
  final String syncState;
  final double? score;
  final String? eudrStatus;
  final DateTime updatedAt;
  const Parcel(
      {required this.id,
      this.serverId,
      this.producerLocalId,
      required this.coopId,
      required this.code,
      required this.geojson,
      required this.areaHa,
      this.plantingYear,
      required this.crop,
      this.gpsAccuracyM,
      required this.collectionMethod,
      required this.collectedAt,
      this.note,
      required this.syncState,
      this.score,
      this.eudrStatus,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    if (!nullToAbsent || serverId != null) {
      map['server_id'] = Variable<String>(serverId);
    }
    if (!nullToAbsent || producerLocalId != null) {
      map['producer_local_id'] = Variable<String>(producerLocalId);
    }
    map['coop_id'] = Variable<String>(coopId);
    map['code'] = Variable<String>(code);
    map['geojson'] = Variable<String>(geojson);
    map['area_ha'] = Variable<double>(areaHa);
    if (!nullToAbsent || plantingYear != null) {
      map['planting_year'] = Variable<int>(plantingYear);
    }
    map['crop'] = Variable<String>(crop);
    if (!nullToAbsent || gpsAccuracyM != null) {
      map['gps_accuracy_m'] = Variable<double>(gpsAccuracyM);
    }
    map['collection_method'] = Variable<String>(collectionMethod);
    map['collected_at'] = Variable<DateTime>(collectedAt);
    if (!nullToAbsent || note != null) {
      map['note'] = Variable<String>(note);
    }
    map['sync_state'] = Variable<String>(syncState);
    if (!nullToAbsent || score != null) {
      map['score'] = Variable<double>(score);
    }
    if (!nullToAbsent || eudrStatus != null) {
      map['eudr_status'] = Variable<String>(eudrStatus);
    }
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  ParcelsCompanion toCompanion(bool nullToAbsent) {
    return ParcelsCompanion(
      id: Value(id),
      serverId: serverId == null && nullToAbsent
          ? const Value.absent()
          : Value(serverId),
      producerLocalId: producerLocalId == null && nullToAbsent
          ? const Value.absent()
          : Value(producerLocalId),
      coopId: Value(coopId),
      code: Value(code),
      geojson: Value(geojson),
      areaHa: Value(areaHa),
      plantingYear: plantingYear == null && nullToAbsent
          ? const Value.absent()
          : Value(plantingYear),
      crop: Value(crop),
      gpsAccuracyM: gpsAccuracyM == null && nullToAbsent
          ? const Value.absent()
          : Value(gpsAccuracyM),
      collectionMethod: Value(collectionMethod),
      collectedAt: Value(collectedAt),
      note: note == null && nullToAbsent ? const Value.absent() : Value(note),
      syncState: Value(syncState),
      score:
          score == null && nullToAbsent ? const Value.absent() : Value(score),
      eudrStatus: eudrStatus == null && nullToAbsent
          ? const Value.absent()
          : Value(eudrStatus),
      updatedAt: Value(updatedAt),
    );
  }

  factory Parcel.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Parcel(
      id: serializer.fromJson<String>(json['id']),
      serverId: serializer.fromJson<String?>(json['serverId']),
      producerLocalId: serializer.fromJson<String?>(json['producerLocalId']),
      coopId: serializer.fromJson<String>(json['coopId']),
      code: serializer.fromJson<String>(json['code']),
      geojson: serializer.fromJson<String>(json['geojson']),
      areaHa: serializer.fromJson<double>(json['areaHa']),
      plantingYear: serializer.fromJson<int?>(json['plantingYear']),
      crop: serializer.fromJson<String>(json['crop']),
      gpsAccuracyM: serializer.fromJson<double?>(json['gpsAccuracyM']),
      collectionMethod: serializer.fromJson<String>(json['collectionMethod']),
      collectedAt: serializer.fromJson<DateTime>(json['collectedAt']),
      note: serializer.fromJson<String?>(json['note']),
      syncState: serializer.fromJson<String>(json['syncState']),
      score: serializer.fromJson<double?>(json['score']),
      eudrStatus: serializer.fromJson<String?>(json['eudrStatus']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'serverId': serializer.toJson<String?>(serverId),
      'producerLocalId': serializer.toJson<String?>(producerLocalId),
      'coopId': serializer.toJson<String>(coopId),
      'code': serializer.toJson<String>(code),
      'geojson': serializer.toJson<String>(geojson),
      'areaHa': serializer.toJson<double>(areaHa),
      'plantingYear': serializer.toJson<int?>(plantingYear),
      'crop': serializer.toJson<String>(crop),
      'gpsAccuracyM': serializer.toJson<double?>(gpsAccuracyM),
      'collectionMethod': serializer.toJson<String>(collectionMethod),
      'collectedAt': serializer.toJson<DateTime>(collectedAt),
      'note': serializer.toJson<String?>(note),
      'syncState': serializer.toJson<String>(syncState),
      'score': serializer.toJson<double?>(score),
      'eudrStatus': serializer.toJson<String?>(eudrStatus),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  Parcel copyWith(
          {String? id,
          Value<String?> serverId = const Value.absent(),
          Value<String?> producerLocalId = const Value.absent(),
          String? coopId,
          String? code,
          String? geojson,
          double? areaHa,
          Value<int?> plantingYear = const Value.absent(),
          String? crop,
          Value<double?> gpsAccuracyM = const Value.absent(),
          String? collectionMethod,
          DateTime? collectedAt,
          Value<String?> note = const Value.absent(),
          String? syncState,
          Value<double?> score = const Value.absent(),
          Value<String?> eudrStatus = const Value.absent(),
          DateTime? updatedAt}) =>
      Parcel(
        id: id ?? this.id,
        serverId: serverId.present ? serverId.value : this.serverId,
        producerLocalId: producerLocalId.present
            ? producerLocalId.value
            : this.producerLocalId,
        coopId: coopId ?? this.coopId,
        code: code ?? this.code,
        geojson: geojson ?? this.geojson,
        areaHa: areaHa ?? this.areaHa,
        plantingYear:
            plantingYear.present ? plantingYear.value : this.plantingYear,
        crop: crop ?? this.crop,
        gpsAccuracyM:
            gpsAccuracyM.present ? gpsAccuracyM.value : this.gpsAccuracyM,
        collectionMethod: collectionMethod ?? this.collectionMethod,
        collectedAt: collectedAt ?? this.collectedAt,
        note: note.present ? note.value : this.note,
        syncState: syncState ?? this.syncState,
        score: score.present ? score.value : this.score,
        eudrStatus: eudrStatus.present ? eudrStatus.value : this.eudrStatus,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  Parcel copyWithCompanion(ParcelsCompanion data) {
    return Parcel(
      id: data.id.present ? data.id.value : this.id,
      serverId: data.serverId.present ? data.serverId.value : this.serverId,
      producerLocalId: data.producerLocalId.present
          ? data.producerLocalId.value
          : this.producerLocalId,
      coopId: data.coopId.present ? data.coopId.value : this.coopId,
      code: data.code.present ? data.code.value : this.code,
      geojson: data.geojson.present ? data.geojson.value : this.geojson,
      areaHa: data.areaHa.present ? data.areaHa.value : this.areaHa,
      plantingYear: data.plantingYear.present
          ? data.plantingYear.value
          : this.plantingYear,
      crop: data.crop.present ? data.crop.value : this.crop,
      gpsAccuracyM: data.gpsAccuracyM.present
          ? data.gpsAccuracyM.value
          : this.gpsAccuracyM,
      collectionMethod: data.collectionMethod.present
          ? data.collectionMethod.value
          : this.collectionMethod,
      collectedAt:
          data.collectedAt.present ? data.collectedAt.value : this.collectedAt,
      note: data.note.present ? data.note.value : this.note,
      syncState: data.syncState.present ? data.syncState.value : this.syncState,
      score: data.score.present ? data.score.value : this.score,
      eudrStatus:
          data.eudrStatus.present ? data.eudrStatus.value : this.eudrStatus,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Parcel(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('producerLocalId: $producerLocalId, ')
          ..write('coopId: $coopId, ')
          ..write('code: $code, ')
          ..write('geojson: $geojson, ')
          ..write('areaHa: $areaHa, ')
          ..write('plantingYear: $plantingYear, ')
          ..write('crop: $crop, ')
          ..write('gpsAccuracyM: $gpsAccuracyM, ')
          ..write('collectionMethod: $collectionMethod, ')
          ..write('collectedAt: $collectedAt, ')
          ..write('note: $note, ')
          ..write('syncState: $syncState, ')
          ..write('score: $score, ')
          ..write('eudrStatus: $eudrStatus, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      serverId,
      producerLocalId,
      coopId,
      code,
      geojson,
      areaHa,
      plantingYear,
      crop,
      gpsAccuracyM,
      collectionMethod,
      collectedAt,
      note,
      syncState,
      score,
      eudrStatus,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Parcel &&
          other.id == this.id &&
          other.serverId == this.serverId &&
          other.producerLocalId == this.producerLocalId &&
          other.coopId == this.coopId &&
          other.code == this.code &&
          other.geojson == this.geojson &&
          other.areaHa == this.areaHa &&
          other.plantingYear == this.plantingYear &&
          other.crop == this.crop &&
          other.gpsAccuracyM == this.gpsAccuracyM &&
          other.collectionMethod == this.collectionMethod &&
          other.collectedAt == this.collectedAt &&
          other.note == this.note &&
          other.syncState == this.syncState &&
          other.score == this.score &&
          other.eudrStatus == this.eudrStatus &&
          other.updatedAt == this.updatedAt);
}

class ParcelsCompanion extends UpdateCompanion<Parcel> {
  final Value<String> id;
  final Value<String?> serverId;
  final Value<String?> producerLocalId;
  final Value<String> coopId;
  final Value<String> code;
  final Value<String> geojson;
  final Value<double> areaHa;
  final Value<int?> plantingYear;
  final Value<String> crop;
  final Value<double?> gpsAccuracyM;
  final Value<String> collectionMethod;
  final Value<DateTime> collectedAt;
  final Value<String?> note;
  final Value<String> syncState;
  final Value<double?> score;
  final Value<String?> eudrStatus;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const ParcelsCompanion({
    this.id = const Value.absent(),
    this.serverId = const Value.absent(),
    this.producerLocalId = const Value.absent(),
    this.coopId = const Value.absent(),
    this.code = const Value.absent(),
    this.geojson = const Value.absent(),
    this.areaHa = const Value.absent(),
    this.plantingYear = const Value.absent(),
    this.crop = const Value.absent(),
    this.gpsAccuracyM = const Value.absent(),
    this.collectionMethod = const Value.absent(),
    this.collectedAt = const Value.absent(),
    this.note = const Value.absent(),
    this.syncState = const Value.absent(),
    this.score = const Value.absent(),
    this.eudrStatus = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ParcelsCompanion.insert({
    required String id,
    this.serverId = const Value.absent(),
    this.producerLocalId = const Value.absent(),
    required String coopId,
    required String code,
    required String geojson,
    this.areaHa = const Value.absent(),
    this.plantingYear = const Value.absent(),
    this.crop = const Value.absent(),
    this.gpsAccuracyM = const Value.absent(),
    this.collectionMethod = const Value.absent(),
    required DateTime collectedAt,
    this.note = const Value.absent(),
    this.syncState = const Value.absent(),
    this.score = const Value.absent(),
    this.eudrStatus = const Value.absent(),
    required DateTime updatedAt,
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        coopId = Value(coopId),
        code = Value(code),
        geojson = Value(geojson),
        collectedAt = Value(collectedAt),
        updatedAt = Value(updatedAt);
  static Insertable<Parcel> custom({
    Expression<String>? id,
    Expression<String>? serverId,
    Expression<String>? producerLocalId,
    Expression<String>? coopId,
    Expression<String>? code,
    Expression<String>? geojson,
    Expression<double>? areaHa,
    Expression<int>? plantingYear,
    Expression<String>? crop,
    Expression<double>? gpsAccuracyM,
    Expression<String>? collectionMethod,
    Expression<DateTime>? collectedAt,
    Expression<String>? note,
    Expression<String>? syncState,
    Expression<double>? score,
    Expression<String>? eudrStatus,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (serverId != null) 'server_id': serverId,
      if (producerLocalId != null) 'producer_local_id': producerLocalId,
      if (coopId != null) 'coop_id': coopId,
      if (code != null) 'code': code,
      if (geojson != null) 'geojson': geojson,
      if (areaHa != null) 'area_ha': areaHa,
      if (plantingYear != null) 'planting_year': plantingYear,
      if (crop != null) 'crop': crop,
      if (gpsAccuracyM != null) 'gps_accuracy_m': gpsAccuracyM,
      if (collectionMethod != null) 'collection_method': collectionMethod,
      if (collectedAt != null) 'collected_at': collectedAt,
      if (note != null) 'note': note,
      if (syncState != null) 'sync_state': syncState,
      if (score != null) 'score': score,
      if (eudrStatus != null) 'eudr_status': eudrStatus,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ParcelsCompanion copyWith(
      {Value<String>? id,
      Value<String?>? serverId,
      Value<String?>? producerLocalId,
      Value<String>? coopId,
      Value<String>? code,
      Value<String>? geojson,
      Value<double>? areaHa,
      Value<int?>? plantingYear,
      Value<String>? crop,
      Value<double?>? gpsAccuracyM,
      Value<String>? collectionMethod,
      Value<DateTime>? collectedAt,
      Value<String?>? note,
      Value<String>? syncState,
      Value<double?>? score,
      Value<String?>? eudrStatus,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return ParcelsCompanion(
      id: id ?? this.id,
      serverId: serverId ?? this.serverId,
      producerLocalId: producerLocalId ?? this.producerLocalId,
      coopId: coopId ?? this.coopId,
      code: code ?? this.code,
      geojson: geojson ?? this.geojson,
      areaHa: areaHa ?? this.areaHa,
      plantingYear: plantingYear ?? this.plantingYear,
      crop: crop ?? this.crop,
      gpsAccuracyM: gpsAccuracyM ?? this.gpsAccuracyM,
      collectionMethod: collectionMethod ?? this.collectionMethod,
      collectedAt: collectedAt ?? this.collectedAt,
      note: note ?? this.note,
      syncState: syncState ?? this.syncState,
      score: score ?? this.score,
      eudrStatus: eudrStatus ?? this.eudrStatus,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (serverId.present) {
      map['server_id'] = Variable<String>(serverId.value);
    }
    if (producerLocalId.present) {
      map['producer_local_id'] = Variable<String>(producerLocalId.value);
    }
    if (coopId.present) {
      map['coop_id'] = Variable<String>(coopId.value);
    }
    if (code.present) {
      map['code'] = Variable<String>(code.value);
    }
    if (geojson.present) {
      map['geojson'] = Variable<String>(geojson.value);
    }
    if (areaHa.present) {
      map['area_ha'] = Variable<double>(areaHa.value);
    }
    if (plantingYear.present) {
      map['planting_year'] = Variable<int>(plantingYear.value);
    }
    if (crop.present) {
      map['crop'] = Variable<String>(crop.value);
    }
    if (gpsAccuracyM.present) {
      map['gps_accuracy_m'] = Variable<double>(gpsAccuracyM.value);
    }
    if (collectionMethod.present) {
      map['collection_method'] = Variable<String>(collectionMethod.value);
    }
    if (collectedAt.present) {
      map['collected_at'] = Variable<DateTime>(collectedAt.value);
    }
    if (note.present) {
      map['note'] = Variable<String>(note.value);
    }
    if (syncState.present) {
      map['sync_state'] = Variable<String>(syncState.value);
    }
    if (score.present) {
      map['score'] = Variable<double>(score.value);
    }
    if (eudrStatus.present) {
      map['eudr_status'] = Variable<String>(eudrStatus.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ParcelsCompanion(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('producerLocalId: $producerLocalId, ')
          ..write('coopId: $coopId, ')
          ..write('code: $code, ')
          ..write('geojson: $geojson, ')
          ..write('areaHa: $areaHa, ')
          ..write('plantingYear: $plantingYear, ')
          ..write('crop: $crop, ')
          ..write('gpsAccuracyM: $gpsAccuracyM, ')
          ..write('collectionMethod: $collectionMethod, ')
          ..write('collectedAt: $collectedAt, ')
          ..write('note: $note, ')
          ..write('syncState: $syncState, ')
          ..write('score: $score, ')
          ..write('eudrStatus: $eudrStatus, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ReferenceDataTable extends ReferenceData
    with TableInfo<$ReferenceDataTable, ReferenceDataData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ReferenceDataTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _keyMeta = const VerificationMeta('key');
  @override
  late final GeneratedColumn<String> key = GeneratedColumn<String>(
      'key', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _jsonMeta = const VerificationMeta('json');
  @override
  late final GeneratedColumn<String> json = GeneratedColumn<String>(
      'json', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _fetchedAtMeta =
      const VerificationMeta('fetchedAt');
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
      'fetched_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [key, json, fetchedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'reference_data';
  @override
  VerificationContext validateIntegrity(Insertable<ReferenceDataData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('key')) {
      context.handle(
          _keyMeta, key.isAcceptableOrUnknown(data['key']!, _keyMeta));
    } else if (isInserting) {
      context.missing(_keyMeta);
    }
    if (data.containsKey('json')) {
      context.handle(
          _jsonMeta, json.isAcceptableOrUnknown(data['json']!, _jsonMeta));
    } else if (isInserting) {
      context.missing(_jsonMeta);
    }
    if (data.containsKey('fetched_at')) {
      context.handle(_fetchedAtMeta,
          fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta));
    } else if (isInserting) {
      context.missing(_fetchedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {key};
  @override
  ReferenceDataData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return ReferenceDataData(
      key: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}key'])!,
      json: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}json'])!,
      fetchedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}fetched_at'])!,
    );
  }

  @override
  $ReferenceDataTable createAlias(String alias) {
    return $ReferenceDataTable(attachedDatabase, alias);
  }
}

class ReferenceDataData extends DataClass
    implements Insertable<ReferenceDataData> {
  final String key;
  final String json;
  final DateTime fetchedAt;
  const ReferenceDataData(
      {required this.key, required this.json, required this.fetchedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['key'] = Variable<String>(key);
    map['json'] = Variable<String>(json);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    return map;
  }

  ReferenceDataCompanion toCompanion(bool nullToAbsent) {
    return ReferenceDataCompanion(
      key: Value(key),
      json: Value(json),
      fetchedAt: Value(fetchedAt),
    );
  }

  factory ReferenceDataData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return ReferenceDataData(
      key: serializer.fromJson<String>(json['key']),
      json: serializer.fromJson<String>(json['json']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'key': serializer.toJson<String>(key),
      'json': serializer.toJson<String>(json),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
    };
  }

  ReferenceDataData copyWith(
          {String? key, String? json, DateTime? fetchedAt}) =>
      ReferenceDataData(
        key: key ?? this.key,
        json: json ?? this.json,
        fetchedAt: fetchedAt ?? this.fetchedAt,
      );
  ReferenceDataData copyWithCompanion(ReferenceDataCompanion data) {
    return ReferenceDataData(
      key: data.key.present ? data.key.value : this.key,
      json: data.json.present ? data.json.value : this.json,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('ReferenceDataData(')
          ..write('key: $key, ')
          ..write('json: $json, ')
          ..write('fetchedAt: $fetchedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(key, json, fetchedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is ReferenceDataData &&
          other.key == this.key &&
          other.json == this.json &&
          other.fetchedAt == this.fetchedAt);
}

class ReferenceDataCompanion extends UpdateCompanion<ReferenceDataData> {
  final Value<String> key;
  final Value<String> json;
  final Value<DateTime> fetchedAt;
  final Value<int> rowid;
  const ReferenceDataCompanion({
    this.key = const Value.absent(),
    this.json = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ReferenceDataCompanion.insert({
    required String key,
    required String json,
    required DateTime fetchedAt,
    this.rowid = const Value.absent(),
  })  : key = Value(key),
        json = Value(json),
        fetchedAt = Value(fetchedAt);
  static Insertable<ReferenceDataData> custom({
    Expression<String>? key,
    Expression<String>? json,
    Expression<DateTime>? fetchedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (key != null) 'key': key,
      if (json != null) 'json': json,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ReferenceDataCompanion copyWith(
      {Value<String>? key,
      Value<String>? json,
      Value<DateTime>? fetchedAt,
      Value<int>? rowid}) {
    return ReferenceDataCompanion(
      key: key ?? this.key,
      json: json ?? this.json,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (key.present) {
      map['key'] = Variable<String>(key.value);
    }
    if (json.present) {
      map['json'] = Variable<String>(json.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ReferenceDataCompanion(')
          ..write('key: $key, ')
          ..write('json: $json, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $SyncQueueTable extends SyncQueue
    with TableInfo<$SyncQueueTable, SyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _entityMeta = const VerificationMeta('entity');
  @override
  late final GeneratedColumn<String> entity = GeneratedColumn<String>(
      'entity', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _opMeta = const VerificationMeta('op');
  @override
  late final GeneratedColumn<String> op = GeneratedColumn<String>(
      'op', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _localIdMeta =
      const VerificationMeta('localId');
  @override
  late final GeneratedColumn<String> localId = GeneratedColumn<String>(
      'local_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _payloadMeta =
      const VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
      'payload', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _attemptsMeta =
      const VerificationMeta('attempts');
  @override
  late final GeneratedColumn<int> attempts = GeneratedColumn<int>(
      'attempts', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _lastErrorMeta =
      const VerificationMeta('lastError');
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
      'last_error', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns =>
      [id, entity, op, localId, payload, createdAt, attempts, lastError];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_queue';
  @override
  VerificationContext validateIntegrity(Insertable<SyncQueueData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('entity')) {
      context.handle(_entityMeta,
          entity.isAcceptableOrUnknown(data['entity']!, _entityMeta));
    } else if (isInserting) {
      context.missing(_entityMeta);
    }
    if (data.containsKey('op')) {
      context.handle(_opMeta, op.isAcceptableOrUnknown(data['op']!, _opMeta));
    } else if (isInserting) {
      context.missing(_opMeta);
    }
    if (data.containsKey('local_id')) {
      context.handle(_localIdMeta,
          localId.isAcceptableOrUnknown(data['local_id']!, _localIdMeta));
    } else if (isInserting) {
      context.missing(_localIdMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    } else if (isInserting) {
      context.missing(_payloadMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('attempts')) {
      context.handle(_attemptsMeta,
          attempts.isAcceptableOrUnknown(data['attempts']!, _attemptsMeta));
    }
    if (data.containsKey('last_error')) {
      context.handle(_lastErrorMeta,
          lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  SyncQueueData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncQueueData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      entity: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity'])!,
      op: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}op'])!,
      localId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}local_id'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      attempts: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}attempts'])!,
      lastError: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}last_error']),
    );
  }

  @override
  $SyncQueueTable createAlias(String alias) {
    return $SyncQueueTable(attachedDatabase, alias);
  }
}

class SyncQueueData extends DataClass implements Insertable<SyncQueueData> {
  final int id;
  final String entity;
  final String op;
  final String localId;
  final String payload;
  final DateTime createdAt;
  final int attempts;
  final String? lastError;
  const SyncQueueData(
      {required this.id,
      required this.entity,
      required this.op,
      required this.localId,
      required this.payload,
      required this.createdAt,
      required this.attempts,
      this.lastError});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['entity'] = Variable<String>(entity);
    map['op'] = Variable<String>(op);
    map['local_id'] = Variable<String>(localId);
    map['payload'] = Variable<String>(payload);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['attempts'] = Variable<int>(attempts);
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    return map;
  }

  SyncQueueCompanion toCompanion(bool nullToAbsent) {
    return SyncQueueCompanion(
      id: Value(id),
      entity: Value(entity),
      op: Value(op),
      localId: Value(localId),
      payload: Value(payload),
      createdAt: Value(createdAt),
      attempts: Value(attempts),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
    );
  }

  factory SyncQueueData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncQueueData(
      id: serializer.fromJson<int>(json['id']),
      entity: serializer.fromJson<String>(json['entity']),
      op: serializer.fromJson<String>(json['op']),
      localId: serializer.fromJson<String>(json['localId']),
      payload: serializer.fromJson<String>(json['payload']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      attempts: serializer.fromJson<int>(json['attempts']),
      lastError: serializer.fromJson<String?>(json['lastError']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'entity': serializer.toJson<String>(entity),
      'op': serializer.toJson<String>(op),
      'localId': serializer.toJson<String>(localId),
      'payload': serializer.toJson<String>(payload),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'attempts': serializer.toJson<int>(attempts),
      'lastError': serializer.toJson<String?>(lastError),
    };
  }

  SyncQueueData copyWith(
          {int? id,
          String? entity,
          String? op,
          String? localId,
          String? payload,
          DateTime? createdAt,
          int? attempts,
          Value<String?> lastError = const Value.absent()}) =>
      SyncQueueData(
        id: id ?? this.id,
        entity: entity ?? this.entity,
        op: op ?? this.op,
        localId: localId ?? this.localId,
        payload: payload ?? this.payload,
        createdAt: createdAt ?? this.createdAt,
        attempts: attempts ?? this.attempts,
        lastError: lastError.present ? lastError.value : this.lastError,
      );
  SyncQueueData copyWithCompanion(SyncQueueCompanion data) {
    return SyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      entity: data.entity.present ? data.entity.value : this.entity,
      op: data.op.present ? data.op.value : this.op,
      localId: data.localId.present ? data.localId.value : this.localId,
      payload: data.payload.present ? data.payload.value : this.payload,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      attempts: data.attempts.present ? data.attempts.value : this.attempts,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueData(')
          ..write('id: $id, ')
          ..write('entity: $entity, ')
          ..write('op: $op, ')
          ..write('localId: $localId, ')
          ..write('payload: $payload, ')
          ..write('createdAt: $createdAt, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, entity, op, localId, payload, createdAt, attempts, lastError);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncQueueData &&
          other.id == this.id &&
          other.entity == this.entity &&
          other.op == this.op &&
          other.localId == this.localId &&
          other.payload == this.payload &&
          other.createdAt == this.createdAt &&
          other.attempts == this.attempts &&
          other.lastError == this.lastError);
}

class SyncQueueCompanion extends UpdateCompanion<SyncQueueData> {
  final Value<int> id;
  final Value<String> entity;
  final Value<String> op;
  final Value<String> localId;
  final Value<String> payload;
  final Value<DateTime> createdAt;
  final Value<int> attempts;
  final Value<String?> lastError;
  const SyncQueueCompanion({
    this.id = const Value.absent(),
    this.entity = const Value.absent(),
    this.op = const Value.absent(),
    this.localId = const Value.absent(),
    this.payload = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
  });
  SyncQueueCompanion.insert({
    this.id = const Value.absent(),
    required String entity,
    required String op,
    required String localId,
    required String payload,
    required DateTime createdAt,
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
  })  : entity = Value(entity),
        op = Value(op),
        localId = Value(localId),
        payload = Value(payload),
        createdAt = Value(createdAt);
  static Insertable<SyncQueueData> custom({
    Expression<int>? id,
    Expression<String>? entity,
    Expression<String>? op,
    Expression<String>? localId,
    Expression<String>? payload,
    Expression<DateTime>? createdAt,
    Expression<int>? attempts,
    Expression<String>? lastError,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (entity != null) 'entity': entity,
      if (op != null) 'op': op,
      if (localId != null) 'local_id': localId,
      if (payload != null) 'payload': payload,
      if (createdAt != null) 'created_at': createdAt,
      if (attempts != null) 'attempts': attempts,
      if (lastError != null) 'last_error': lastError,
    });
  }

  SyncQueueCompanion copyWith(
      {Value<int>? id,
      Value<String>? entity,
      Value<String>? op,
      Value<String>? localId,
      Value<String>? payload,
      Value<DateTime>? createdAt,
      Value<int>? attempts,
      Value<String?>? lastError}) {
    return SyncQueueCompanion(
      id: id ?? this.id,
      entity: entity ?? this.entity,
      op: op ?? this.op,
      localId: localId ?? this.localId,
      payload: payload ?? this.payload,
      createdAt: createdAt ?? this.createdAt,
      attempts: attempts ?? this.attempts,
      lastError: lastError ?? this.lastError,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (entity.present) {
      map['entity'] = Variable<String>(entity.value);
    }
    if (op.present) {
      map['op'] = Variable<String>(op.value);
    }
    if (localId.present) {
      map['local_id'] = Variable<String>(localId.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (attempts.present) {
      map['attempts'] = Variable<int>(attempts.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('entity: $entity, ')
          ..write('op: $op, ')
          ..write('localId: $localId, ')
          ..write('payload: $payload, ')
          ..write('createdAt: $createdAt, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError')
          ..write(')'))
        .toString();
  }
}

class $OutboxLogTable extends OutboxLog
    with TableInfo<$OutboxLogTable, OutboxLogData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $OutboxLogTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _batchIdMeta =
      const VerificationMeta('batchId');
  @override
  late final GeneratedColumn<String> batchId = GeneratedColumn<String>(
      'batch_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _sentAtMeta = const VerificationMeta('sentAt');
  @override
  late final GeneratedColumn<DateTime> sentAt = GeneratedColumn<DateTime>(
      'sent_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _acceptedMeta =
      const VerificationMeta('accepted');
  @override
  late final GeneratedColumn<int> accepted = GeneratedColumn<int>(
      'accepted', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _rejectedMeta =
      const VerificationMeta('rejected');
  @override
  late final GeneratedColumn<int> rejected = GeneratedColumn<int>(
      'rejected', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _responseMeta =
      const VerificationMeta('response');
  @override
  late final GeneratedColumn<String> response = GeneratedColumn<String>(
      'response', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns =>
      [id, batchId, sentAt, accepted, rejected, response];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'outbox_log';
  @override
  VerificationContext validateIntegrity(Insertable<OutboxLogData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('batch_id')) {
      context.handle(_batchIdMeta,
          batchId.isAcceptableOrUnknown(data['batch_id']!, _batchIdMeta));
    }
    if (data.containsKey('sent_at')) {
      context.handle(_sentAtMeta,
          sentAt.isAcceptableOrUnknown(data['sent_at']!, _sentAtMeta));
    } else if (isInserting) {
      context.missing(_sentAtMeta);
    }
    if (data.containsKey('accepted')) {
      context.handle(_acceptedMeta,
          accepted.isAcceptableOrUnknown(data['accepted']!, _acceptedMeta));
    }
    if (data.containsKey('rejected')) {
      context.handle(_rejectedMeta,
          rejected.isAcceptableOrUnknown(data['rejected']!, _rejectedMeta));
    }
    if (data.containsKey('response')) {
      context.handle(_responseMeta,
          response.isAcceptableOrUnknown(data['response']!, _responseMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  OutboxLogData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return OutboxLogData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      batchId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}batch_id']),
      sentAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}sent_at'])!,
      accepted: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}accepted'])!,
      rejected: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}rejected'])!,
      response: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}response']),
    );
  }

  @override
  $OutboxLogTable createAlias(String alias) {
    return $OutboxLogTable(attachedDatabase, alias);
  }
}

class OutboxLogData extends DataClass implements Insertable<OutboxLogData> {
  final int id;
  final String? batchId;
  final DateTime sentAt;
  final int accepted;
  final int rejected;
  final String? response;
  const OutboxLogData(
      {required this.id,
      this.batchId,
      required this.sentAt,
      required this.accepted,
      required this.rejected,
      this.response});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    if (!nullToAbsent || batchId != null) {
      map['batch_id'] = Variable<String>(batchId);
    }
    map['sent_at'] = Variable<DateTime>(sentAt);
    map['accepted'] = Variable<int>(accepted);
    map['rejected'] = Variable<int>(rejected);
    if (!nullToAbsent || response != null) {
      map['response'] = Variable<String>(response);
    }
    return map;
  }

  OutboxLogCompanion toCompanion(bool nullToAbsent) {
    return OutboxLogCompanion(
      id: Value(id),
      batchId: batchId == null && nullToAbsent
          ? const Value.absent()
          : Value(batchId),
      sentAt: Value(sentAt),
      accepted: Value(accepted),
      rejected: Value(rejected),
      response: response == null && nullToAbsent
          ? const Value.absent()
          : Value(response),
    );
  }

  factory OutboxLogData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return OutboxLogData(
      id: serializer.fromJson<int>(json['id']),
      batchId: serializer.fromJson<String?>(json['batchId']),
      sentAt: serializer.fromJson<DateTime>(json['sentAt']),
      accepted: serializer.fromJson<int>(json['accepted']),
      rejected: serializer.fromJson<int>(json['rejected']),
      response: serializer.fromJson<String?>(json['response']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'batchId': serializer.toJson<String?>(batchId),
      'sentAt': serializer.toJson<DateTime>(sentAt),
      'accepted': serializer.toJson<int>(accepted),
      'rejected': serializer.toJson<int>(rejected),
      'response': serializer.toJson<String?>(response),
    };
  }

  OutboxLogData copyWith(
          {int? id,
          Value<String?> batchId = const Value.absent(),
          DateTime? sentAt,
          int? accepted,
          int? rejected,
          Value<String?> response = const Value.absent()}) =>
      OutboxLogData(
        id: id ?? this.id,
        batchId: batchId.present ? batchId.value : this.batchId,
        sentAt: sentAt ?? this.sentAt,
        accepted: accepted ?? this.accepted,
        rejected: rejected ?? this.rejected,
        response: response.present ? response.value : this.response,
      );
  OutboxLogData copyWithCompanion(OutboxLogCompanion data) {
    return OutboxLogData(
      id: data.id.present ? data.id.value : this.id,
      batchId: data.batchId.present ? data.batchId.value : this.batchId,
      sentAt: data.sentAt.present ? data.sentAt.value : this.sentAt,
      accepted: data.accepted.present ? data.accepted.value : this.accepted,
      rejected: data.rejected.present ? data.rejected.value : this.rejected,
      response: data.response.present ? data.response.value : this.response,
    );
  }

  @override
  String toString() {
    return (StringBuffer('OutboxLogData(')
          ..write('id: $id, ')
          ..write('batchId: $batchId, ')
          ..write('sentAt: $sentAt, ')
          ..write('accepted: $accepted, ')
          ..write('rejected: $rejected, ')
          ..write('response: $response')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, batchId, sentAt, accepted, rejected, response);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is OutboxLogData &&
          other.id == this.id &&
          other.batchId == this.batchId &&
          other.sentAt == this.sentAt &&
          other.accepted == this.accepted &&
          other.rejected == this.rejected &&
          other.response == this.response);
}

class OutboxLogCompanion extends UpdateCompanion<OutboxLogData> {
  final Value<int> id;
  final Value<String?> batchId;
  final Value<DateTime> sentAt;
  final Value<int> accepted;
  final Value<int> rejected;
  final Value<String?> response;
  const OutboxLogCompanion({
    this.id = const Value.absent(),
    this.batchId = const Value.absent(),
    this.sentAt = const Value.absent(),
    this.accepted = const Value.absent(),
    this.rejected = const Value.absent(),
    this.response = const Value.absent(),
  });
  OutboxLogCompanion.insert({
    this.id = const Value.absent(),
    this.batchId = const Value.absent(),
    required DateTime sentAt,
    this.accepted = const Value.absent(),
    this.rejected = const Value.absent(),
    this.response = const Value.absent(),
  }) : sentAt = Value(sentAt);
  static Insertable<OutboxLogData> custom({
    Expression<int>? id,
    Expression<String>? batchId,
    Expression<DateTime>? sentAt,
    Expression<int>? accepted,
    Expression<int>? rejected,
    Expression<String>? response,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (batchId != null) 'batch_id': batchId,
      if (sentAt != null) 'sent_at': sentAt,
      if (accepted != null) 'accepted': accepted,
      if (rejected != null) 'rejected': rejected,
      if (response != null) 'response': response,
    });
  }

  OutboxLogCompanion copyWith(
      {Value<int>? id,
      Value<String?>? batchId,
      Value<DateTime>? sentAt,
      Value<int>? accepted,
      Value<int>? rejected,
      Value<String?>? response}) {
    return OutboxLogCompanion(
      id: id ?? this.id,
      batchId: batchId ?? this.batchId,
      sentAt: sentAt ?? this.sentAt,
      accepted: accepted ?? this.accepted,
      rejected: rejected ?? this.rejected,
      response: response ?? this.response,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (batchId.present) {
      map['batch_id'] = Variable<String>(batchId.value);
    }
    if (sentAt.present) {
      map['sent_at'] = Variable<DateTime>(sentAt.value);
    }
    if (accepted.present) {
      map['accepted'] = Variable<int>(accepted.value);
    }
    if (rejected.present) {
      map['rejected'] = Variable<int>(rejected.value);
    }
    if (response.present) {
      map['response'] = Variable<String>(response.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('OutboxLogCompanion(')
          ..write('id: $id, ')
          ..write('batchId: $batchId, ')
          ..write('sentAt: $sentAt, ')
          ..write('accepted: $accepted, ')
          ..write('rejected: $rejected, ')
          ..write('response: $response')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $ProducersTable producers = $ProducersTable(this);
  late final $ParcelsTable parcels = $ParcelsTable(this);
  late final $ReferenceDataTable referenceData = $ReferenceDataTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  late final $OutboxLogTable outboxLog = $OutboxLogTable(this);
  late final ProducerDao producerDao = ProducerDao(this as AppDatabase);
  late final ParcelDao parcelDao = ParcelDao(this as AppDatabase);
  late final SyncDao syncDao = SyncDao(this as AppDatabase);
  late final ReferenceDao referenceDao = ReferenceDao(this as AppDatabase);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities =>
      [producers, parcels, referenceData, syncQueue, outboxLog];
}

typedef $$ProducersTableCreateCompanionBuilder = ProducersCompanion Function({
  required String id,
  Value<String?> serverId,
  required String coopId,
  required String fullName,
  Value<String?> nationalId,
  Value<String> gender,
  Value<String?> village,
  Value<String?> phone,
  Value<DateTime?> registeredAt,
  Value<bool> dirty,
  Value<bool> deleted,
  required DateTime updatedAt,
  Value<int> rowid,
});
typedef $$ProducersTableUpdateCompanionBuilder = ProducersCompanion Function({
  Value<String> id,
  Value<String?> serverId,
  Value<String> coopId,
  Value<String> fullName,
  Value<String?> nationalId,
  Value<String> gender,
  Value<String?> village,
  Value<String?> phone,
  Value<DateTime?> registeredAt,
  Value<bool> dirty,
  Value<bool> deleted,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

class $$ProducersTableFilterComposer
    extends Composer<_$AppDatabase, $ProducersTable> {
  $$ProducersTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get coopId => $composableBuilder(
      column: $table.coopId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get fullName => $composableBuilder(
      column: $table.fullName, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nationalId => $composableBuilder(
      column: $table.nationalId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get gender => $composableBuilder(
      column: $table.gender, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get village => $composableBuilder(
      column: $table.village, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get phone => $composableBuilder(
      column: $table.phone, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get registeredAt => $composableBuilder(
      column: $table.registeredAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get dirty => $composableBuilder(
      column: $table.dirty, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get deleted => $composableBuilder(
      column: $table.deleted, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));
}

class $$ProducersTableOrderingComposer
    extends Composer<_$AppDatabase, $ProducersTable> {
  $$ProducersTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get coopId => $composableBuilder(
      column: $table.coopId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get fullName => $composableBuilder(
      column: $table.fullName, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nationalId => $composableBuilder(
      column: $table.nationalId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get gender => $composableBuilder(
      column: $table.gender, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get village => $composableBuilder(
      column: $table.village, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get phone => $composableBuilder(
      column: $table.phone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get registeredAt => $composableBuilder(
      column: $table.registeredAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get dirty => $composableBuilder(
      column: $table.dirty, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get deleted => $composableBuilder(
      column: $table.deleted, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$ProducersTableAnnotationComposer
    extends Composer<_$AppDatabase, $ProducersTable> {
  $$ProducersTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get serverId =>
      $composableBuilder(column: $table.serverId, builder: (column) => column);

  GeneratedColumn<String> get coopId =>
      $composableBuilder(column: $table.coopId, builder: (column) => column);

  GeneratedColumn<String> get fullName =>
      $composableBuilder(column: $table.fullName, builder: (column) => column);

  GeneratedColumn<String> get nationalId => $composableBuilder(
      column: $table.nationalId, builder: (column) => column);

  GeneratedColumn<String> get gender =>
      $composableBuilder(column: $table.gender, builder: (column) => column);

  GeneratedColumn<String> get village =>
      $composableBuilder(column: $table.village, builder: (column) => column);

  GeneratedColumn<String> get phone =>
      $composableBuilder(column: $table.phone, builder: (column) => column);

  GeneratedColumn<DateTime> get registeredAt => $composableBuilder(
      column: $table.registeredAt, builder: (column) => column);

  GeneratedColumn<bool> get dirty =>
      $composableBuilder(column: $table.dirty, builder: (column) => column);

  GeneratedColumn<bool> get deleted =>
      $composableBuilder(column: $table.deleted, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$ProducersTableTableManager extends RootTableManager<
    _$AppDatabase,
    $ProducersTable,
    Producer,
    $$ProducersTableFilterComposer,
    $$ProducersTableOrderingComposer,
    $$ProducersTableAnnotationComposer,
    $$ProducersTableCreateCompanionBuilder,
    $$ProducersTableUpdateCompanionBuilder,
    (Producer, BaseReferences<_$AppDatabase, $ProducersTable, Producer>),
    Producer,
    PrefetchHooks Function()> {
  $$ProducersTableTableManager(_$AppDatabase db, $ProducersTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ProducersTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ProducersTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ProducersTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String> coopId = const Value.absent(),
            Value<String> fullName = const Value.absent(),
            Value<String?> nationalId = const Value.absent(),
            Value<String> gender = const Value.absent(),
            Value<String?> village = const Value.absent(),
            Value<String?> phone = const Value.absent(),
            Value<DateTime?> registeredAt = const Value.absent(),
            Value<bool> dirty = const Value.absent(),
            Value<bool> deleted = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ProducersCompanion(
            id: id,
            serverId: serverId,
            coopId: coopId,
            fullName: fullName,
            nationalId: nationalId,
            gender: gender,
            village: village,
            phone: phone,
            registeredAt: registeredAt,
            dirty: dirty,
            deleted: deleted,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            Value<String?> serverId = const Value.absent(),
            required String coopId,
            required String fullName,
            Value<String?> nationalId = const Value.absent(),
            Value<String> gender = const Value.absent(),
            Value<String?> village = const Value.absent(),
            Value<String?> phone = const Value.absent(),
            Value<DateTime?> registeredAt = const Value.absent(),
            Value<bool> dirty = const Value.absent(),
            Value<bool> deleted = const Value.absent(),
            required DateTime updatedAt,
            Value<int> rowid = const Value.absent(),
          }) =>
              ProducersCompanion.insert(
            id: id,
            serverId: serverId,
            coopId: coopId,
            fullName: fullName,
            nationalId: nationalId,
            gender: gender,
            village: village,
            phone: phone,
            registeredAt: registeredAt,
            dirty: dirty,
            deleted: deleted,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$ProducersTable, Producer>(table),
                    BaseReferences<_$AppDatabase, $ProducersTable, Producer>(
                        db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$ProducersTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $ProducersTable,
    Producer,
    $$ProducersTableFilterComposer,
    $$ProducersTableOrderingComposer,
    $$ProducersTableAnnotationComposer,
    $$ProducersTableCreateCompanionBuilder,
    $$ProducersTableUpdateCompanionBuilder,
    (Producer, BaseReferences<_$AppDatabase, $ProducersTable, Producer>),
    Producer,
    PrefetchHooks Function()>;
typedef $$ParcelsTableCreateCompanionBuilder = ParcelsCompanion Function({
  required String id,
  Value<String?> serverId,
  Value<String?> producerLocalId,
  required String coopId,
  required String code,
  required String geojson,
  Value<double> areaHa,
  Value<int?> plantingYear,
  Value<String> crop,
  Value<double?> gpsAccuracyM,
  Value<String> collectionMethod,
  required DateTime collectedAt,
  Value<String?> note,
  Value<String> syncState,
  Value<double?> score,
  Value<String?> eudrStatus,
  required DateTime updatedAt,
  Value<int> rowid,
});
typedef $$ParcelsTableUpdateCompanionBuilder = ParcelsCompanion Function({
  Value<String> id,
  Value<String?> serverId,
  Value<String?> producerLocalId,
  Value<String> coopId,
  Value<String> code,
  Value<String> geojson,
  Value<double> areaHa,
  Value<int?> plantingYear,
  Value<String> crop,
  Value<double?> gpsAccuracyM,
  Value<String> collectionMethod,
  Value<DateTime> collectedAt,
  Value<String?> note,
  Value<String> syncState,
  Value<double?> score,
  Value<String?> eudrStatus,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

class $$ParcelsTableFilterComposer
    extends Composer<_$AppDatabase, $ParcelsTable> {
  $$ParcelsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get producerLocalId => $composableBuilder(
      column: $table.producerLocalId,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get coopId => $composableBuilder(
      column: $table.coopId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get code => $composableBuilder(
      column: $table.code, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get geojson => $composableBuilder(
      column: $table.geojson, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get areaHa => $composableBuilder(
      column: $table.areaHa, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get plantingYear => $composableBuilder(
      column: $table.plantingYear, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get crop => $composableBuilder(
      column: $table.crop, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get collectionMethod => $composableBuilder(
      column: $table.collectionMethod,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get collectedAt => $composableBuilder(
      column: $table.collectedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get syncState => $composableBuilder(
      column: $table.syncState, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get eudrStatus => $composableBuilder(
      column: $table.eudrStatus, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));
}

class $$ParcelsTableOrderingComposer
    extends Composer<_$AppDatabase, $ParcelsTable> {
  $$ParcelsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get producerLocalId => $composableBuilder(
      column: $table.producerLocalId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get coopId => $composableBuilder(
      column: $table.coopId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get code => $composableBuilder(
      column: $table.code, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get geojson => $composableBuilder(
      column: $table.geojson, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get areaHa => $composableBuilder(
      column: $table.areaHa, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get plantingYear => $composableBuilder(
      column: $table.plantingYear,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get crop => $composableBuilder(
      column: $table.crop, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get collectionMethod => $composableBuilder(
      column: $table.collectionMethod,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get collectedAt => $composableBuilder(
      column: $table.collectedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get syncState => $composableBuilder(
      column: $table.syncState, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get eudrStatus => $composableBuilder(
      column: $table.eudrStatus, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$ParcelsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ParcelsTable> {
  $$ParcelsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get serverId =>
      $composableBuilder(column: $table.serverId, builder: (column) => column);

  GeneratedColumn<String> get producerLocalId => $composableBuilder(
      column: $table.producerLocalId, builder: (column) => column);

  GeneratedColumn<String> get coopId =>
      $composableBuilder(column: $table.coopId, builder: (column) => column);

  GeneratedColumn<String> get code =>
      $composableBuilder(column: $table.code, builder: (column) => column);

  GeneratedColumn<String> get geojson =>
      $composableBuilder(column: $table.geojson, builder: (column) => column);

  GeneratedColumn<double> get areaHa =>
      $composableBuilder(column: $table.areaHa, builder: (column) => column);

  GeneratedColumn<int> get plantingYear => $composableBuilder(
      column: $table.plantingYear, builder: (column) => column);

  GeneratedColumn<String> get crop =>
      $composableBuilder(column: $table.crop, builder: (column) => column);

  GeneratedColumn<double> get gpsAccuracyM => $composableBuilder(
      column: $table.gpsAccuracyM, builder: (column) => column);

  GeneratedColumn<String> get collectionMethod => $composableBuilder(
      column: $table.collectionMethod, builder: (column) => column);

  GeneratedColumn<DateTime> get collectedAt => $composableBuilder(
      column: $table.collectedAt, builder: (column) => column);

  GeneratedColumn<String> get note =>
      $composableBuilder(column: $table.note, builder: (column) => column);

  GeneratedColumn<String> get syncState =>
      $composableBuilder(column: $table.syncState, builder: (column) => column);

  GeneratedColumn<double> get score =>
      $composableBuilder(column: $table.score, builder: (column) => column);

  GeneratedColumn<String> get eudrStatus => $composableBuilder(
      column: $table.eudrStatus, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$ParcelsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $ParcelsTable,
    Parcel,
    $$ParcelsTableFilterComposer,
    $$ParcelsTableOrderingComposer,
    $$ParcelsTableAnnotationComposer,
    $$ParcelsTableCreateCompanionBuilder,
    $$ParcelsTableUpdateCompanionBuilder,
    (Parcel, BaseReferences<_$AppDatabase, $ParcelsTable, Parcel>),
    Parcel,
    PrefetchHooks Function()> {
  $$ParcelsTableTableManager(_$AppDatabase db, $ParcelsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ParcelsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ParcelsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ParcelsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String?> serverId = const Value.absent(),
            Value<String?> producerLocalId = const Value.absent(),
            Value<String> coopId = const Value.absent(),
            Value<String> code = const Value.absent(),
            Value<String> geojson = const Value.absent(),
            Value<double> areaHa = const Value.absent(),
            Value<int?> plantingYear = const Value.absent(),
            Value<String> crop = const Value.absent(),
            Value<double?> gpsAccuracyM = const Value.absent(),
            Value<String> collectionMethod = const Value.absent(),
            Value<DateTime> collectedAt = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<String> syncState = const Value.absent(),
            Value<double?> score = const Value.absent(),
            Value<String?> eudrStatus = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ParcelsCompanion(
            id: id,
            serverId: serverId,
            producerLocalId: producerLocalId,
            coopId: coopId,
            code: code,
            geojson: geojson,
            areaHa: areaHa,
            plantingYear: plantingYear,
            crop: crop,
            gpsAccuracyM: gpsAccuracyM,
            collectionMethod: collectionMethod,
            collectedAt: collectedAt,
            note: note,
            syncState: syncState,
            score: score,
            eudrStatus: eudrStatus,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            Value<String?> serverId = const Value.absent(),
            Value<String?> producerLocalId = const Value.absent(),
            required String coopId,
            required String code,
            required String geojson,
            Value<double> areaHa = const Value.absent(),
            Value<int?> plantingYear = const Value.absent(),
            Value<String> crop = const Value.absent(),
            Value<double?> gpsAccuracyM = const Value.absent(),
            Value<String> collectionMethod = const Value.absent(),
            required DateTime collectedAt,
            Value<String?> note = const Value.absent(),
            Value<String> syncState = const Value.absent(),
            Value<double?> score = const Value.absent(),
            Value<String?> eudrStatus = const Value.absent(),
            required DateTime updatedAt,
            Value<int> rowid = const Value.absent(),
          }) =>
              ParcelsCompanion.insert(
            id: id,
            serverId: serverId,
            producerLocalId: producerLocalId,
            coopId: coopId,
            code: code,
            geojson: geojson,
            areaHa: areaHa,
            plantingYear: plantingYear,
            crop: crop,
            gpsAccuracyM: gpsAccuracyM,
            collectionMethod: collectionMethod,
            collectedAt: collectedAt,
            note: note,
            syncState: syncState,
            score: score,
            eudrStatus: eudrStatus,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$ParcelsTable, Parcel>(table),
                    BaseReferences<_$AppDatabase, $ParcelsTable, Parcel>(
                        db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$ParcelsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $ParcelsTable,
    Parcel,
    $$ParcelsTableFilterComposer,
    $$ParcelsTableOrderingComposer,
    $$ParcelsTableAnnotationComposer,
    $$ParcelsTableCreateCompanionBuilder,
    $$ParcelsTableUpdateCompanionBuilder,
    (Parcel, BaseReferences<_$AppDatabase, $ParcelsTable, Parcel>),
    Parcel,
    PrefetchHooks Function()>;
typedef $$ReferenceDataTableCreateCompanionBuilder = ReferenceDataCompanion
    Function({
  required String key,
  required String json,
  required DateTime fetchedAt,
  Value<int> rowid,
});
typedef $$ReferenceDataTableUpdateCompanionBuilder = ReferenceDataCompanion
    Function({
  Value<String> key,
  Value<String> json,
  Value<DateTime> fetchedAt,
  Value<int> rowid,
});

class $$ReferenceDataTableFilterComposer
    extends Composer<_$AppDatabase, $ReferenceDataTable> {
  $$ReferenceDataTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get key => $composableBuilder(
      column: $table.key, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get json => $composableBuilder(
      column: $table.json, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
      column: $table.fetchedAt, builder: (column) => ColumnFilters(column));
}

class $$ReferenceDataTableOrderingComposer
    extends Composer<_$AppDatabase, $ReferenceDataTable> {
  $$ReferenceDataTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get key => $composableBuilder(
      column: $table.key, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get json => $composableBuilder(
      column: $table.json, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
      column: $table.fetchedAt, builder: (column) => ColumnOrderings(column));
}

class $$ReferenceDataTableAnnotationComposer
    extends Composer<_$AppDatabase, $ReferenceDataTable> {
  $$ReferenceDataTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get key =>
      $composableBuilder(column: $table.key, builder: (column) => column);

  GeneratedColumn<String> get json =>
      $composableBuilder(column: $table.json, builder: (column) => column);

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);
}

class $$ReferenceDataTableTableManager extends RootTableManager<
    _$AppDatabase,
    $ReferenceDataTable,
    ReferenceDataData,
    $$ReferenceDataTableFilterComposer,
    $$ReferenceDataTableOrderingComposer,
    $$ReferenceDataTableAnnotationComposer,
    $$ReferenceDataTableCreateCompanionBuilder,
    $$ReferenceDataTableUpdateCompanionBuilder,
    (
      ReferenceDataData,
      BaseReferences<_$AppDatabase, $ReferenceDataTable, ReferenceDataData>
    ),
    ReferenceDataData,
    PrefetchHooks Function()> {
  $$ReferenceDataTableTableManager(_$AppDatabase db, $ReferenceDataTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ReferenceDataTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ReferenceDataTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ReferenceDataTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> key = const Value.absent(),
            Value<String> json = const Value.absent(),
            Value<DateTime> fetchedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ReferenceDataCompanion(
            key: key,
            json: json,
            fetchedAt: fetchedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String key,
            required String json,
            required DateTime fetchedAt,
            Value<int> rowid = const Value.absent(),
          }) =>
              ReferenceDataCompanion.insert(
            key: key,
            json: json,
            fetchedAt: fetchedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$ReferenceDataTable, ReferenceDataData>(table),
                    BaseReferences<_$AppDatabase, $ReferenceDataTable,
                        ReferenceDataData>(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$ReferenceDataTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $ReferenceDataTable,
    ReferenceDataData,
    $$ReferenceDataTableFilterComposer,
    $$ReferenceDataTableOrderingComposer,
    $$ReferenceDataTableAnnotationComposer,
    $$ReferenceDataTableCreateCompanionBuilder,
    $$ReferenceDataTableUpdateCompanionBuilder,
    (
      ReferenceDataData,
      BaseReferences<_$AppDatabase, $ReferenceDataTable, ReferenceDataData>
    ),
    ReferenceDataData,
    PrefetchHooks Function()>;
typedef $$SyncQueueTableCreateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  required String entity,
  required String op,
  required String localId,
  required String payload,
  required DateTime createdAt,
  Value<int> attempts,
  Value<String?> lastError,
});
typedef $$SyncQueueTableUpdateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  Value<String> entity,
  Value<String> op,
  Value<String> localId,
  Value<String> payload,
  Value<DateTime> createdAt,
  Value<int> attempts,
  Value<String?> lastError,
});

class $$SyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entity => $composableBuilder(
      column: $table.entity, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get op => $composableBuilder(
      column: $table.op, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get localId => $composableBuilder(
      column: $table.localId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get attempts => $composableBuilder(
      column: $table.attempts, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnFilters(column));
}

class $$SyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entity => $composableBuilder(
      column: $table.entity, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get op => $composableBuilder(
      column: $table.op, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get localId => $composableBuilder(
      column: $table.localId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get attempts => $composableBuilder(
      column: $table.attempts, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get lastError => $composableBuilder(
      column: $table.lastError, builder: (column) => ColumnOrderings(column));
}

class $$SyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get entity =>
      $composableBuilder(column: $table.entity, builder: (column) => column);

  GeneratedColumn<String> get op =>
      $composableBuilder(column: $table.op, builder: (column) => column);

  GeneratedColumn<String> get localId =>
      $composableBuilder(column: $table.localId, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<int> get attempts =>
      $composableBuilder(column: $table.attempts, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);
}

class $$SyncQueueTableTableManager extends RootTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()> {
  $$SyncQueueTableTableManager(_$AppDatabase db, $SyncQueueTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncQueueTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncQueueTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> entity = const Value.absent(),
            Value<String> op = const Value.absent(),
            Value<String> localId = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> attempts = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
          }) =>
              SyncQueueCompanion(
            id: id,
            entity: entity,
            op: op,
            localId: localId,
            payload: payload,
            createdAt: createdAt,
            attempts: attempts,
            lastError: lastError,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String entity,
            required String op,
            required String localId,
            required String payload,
            required DateTime createdAt,
            Value<int> attempts = const Value.absent(),
            Value<String?> lastError = const Value.absent(),
          }) =>
              SyncQueueCompanion.insert(
            id: id,
            entity: entity,
            op: op,
            localId: localId,
            payload: payload,
            createdAt: createdAt,
            attempts: attempts,
            lastError: lastError,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$SyncQueueTable, SyncQueueData>(table),
                    BaseReferences<_$AppDatabase, $SyncQueueTable,
                        SyncQueueData>(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncQueueTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()>;
typedef $$OutboxLogTableCreateCompanionBuilder = OutboxLogCompanion Function({
  Value<int> id,
  Value<String?> batchId,
  required DateTime sentAt,
  Value<int> accepted,
  Value<int> rejected,
  Value<String?> response,
});
typedef $$OutboxLogTableUpdateCompanionBuilder = OutboxLogCompanion Function({
  Value<int> id,
  Value<String?> batchId,
  Value<DateTime> sentAt,
  Value<int> accepted,
  Value<int> rejected,
  Value<String?> response,
});

class $$OutboxLogTableFilterComposer
    extends Composer<_$AppDatabase, $OutboxLogTable> {
  $$OutboxLogTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get batchId => $composableBuilder(
      column: $table.batchId, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get sentAt => $composableBuilder(
      column: $table.sentAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get accepted => $composableBuilder(
      column: $table.accepted, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get rejected => $composableBuilder(
      column: $table.rejected, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get response => $composableBuilder(
      column: $table.response, builder: (column) => ColumnFilters(column));
}

class $$OutboxLogTableOrderingComposer
    extends Composer<_$AppDatabase, $OutboxLogTable> {
  $$OutboxLogTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get batchId => $composableBuilder(
      column: $table.batchId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get sentAt => $composableBuilder(
      column: $table.sentAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get accepted => $composableBuilder(
      column: $table.accepted, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get rejected => $composableBuilder(
      column: $table.rejected, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get response => $composableBuilder(
      column: $table.response, builder: (column) => ColumnOrderings(column));
}

class $$OutboxLogTableAnnotationComposer
    extends Composer<_$AppDatabase, $OutboxLogTable> {
  $$OutboxLogTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get batchId =>
      $composableBuilder(column: $table.batchId, builder: (column) => column);

  GeneratedColumn<DateTime> get sentAt =>
      $composableBuilder(column: $table.sentAt, builder: (column) => column);

  GeneratedColumn<int> get accepted =>
      $composableBuilder(column: $table.accepted, builder: (column) => column);

  GeneratedColumn<int> get rejected =>
      $composableBuilder(column: $table.rejected, builder: (column) => column);

  GeneratedColumn<String> get response =>
      $composableBuilder(column: $table.response, builder: (column) => column);
}

class $$OutboxLogTableTableManager extends RootTableManager<
    _$AppDatabase,
    $OutboxLogTable,
    OutboxLogData,
    $$OutboxLogTableFilterComposer,
    $$OutboxLogTableOrderingComposer,
    $$OutboxLogTableAnnotationComposer,
    $$OutboxLogTableCreateCompanionBuilder,
    $$OutboxLogTableUpdateCompanionBuilder,
    (
      OutboxLogData,
      BaseReferences<_$AppDatabase, $OutboxLogTable, OutboxLogData>
    ),
    OutboxLogData,
    PrefetchHooks Function()> {
  $$OutboxLogTableTableManager(_$AppDatabase db, $OutboxLogTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$OutboxLogTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$OutboxLogTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$OutboxLogTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String?> batchId = const Value.absent(),
            Value<DateTime> sentAt = const Value.absent(),
            Value<int> accepted = const Value.absent(),
            Value<int> rejected = const Value.absent(),
            Value<String?> response = const Value.absent(),
          }) =>
              OutboxLogCompanion(
            id: id,
            batchId: batchId,
            sentAt: sentAt,
            accepted: accepted,
            rejected: rejected,
            response: response,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String?> batchId = const Value.absent(),
            required DateTime sentAt,
            Value<int> accepted = const Value.absent(),
            Value<int> rejected = const Value.absent(),
            Value<String?> response = const Value.absent(),
          }) =>
              OutboxLogCompanion.insert(
            id: id,
            batchId: batchId,
            sentAt: sentAt,
            accepted: accepted,
            rejected: rejected,
            response: response,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable<$OutboxLogTable, OutboxLogData>(table),
                    BaseReferences<_$AppDatabase, $OutboxLogTable,
                        OutboxLogData>(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$OutboxLogTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $OutboxLogTable,
    OutboxLogData,
    $$OutboxLogTableFilterComposer,
    $$OutboxLogTableOrderingComposer,
    $$OutboxLogTableAnnotationComposer,
    $$OutboxLogTableCreateCompanionBuilder,
    $$OutboxLogTableUpdateCompanionBuilder,
    (
      OutboxLogData,
      BaseReferences<_$AppDatabase, $OutboxLogTable, OutboxLogData>
    ),
    OutboxLogData,
    PrefetchHooks Function()>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$ProducersTableTableManager get producers =>
      $$ProducersTableTableManager(_db, _db.producers);
  $$ParcelsTableTableManager get parcels =>
      $$ParcelsTableTableManager(_db, _db.parcels);
  $$ReferenceDataTableTableManager get referenceData =>
      $$ReferenceDataTableTableManager(_db, _db.referenceData);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
  $$OutboxLogTableTableManager get outboxLog =>
      $$OutboxLogTableTableManager(_db, _db.outboxLog);
}

mixin _$ProducerDaoMixin on DatabaseAccessor<AppDatabase> {
  $ProducersTable get producers => attachedDatabase.producers;
  ProducerDaoManager get managers => ProducerDaoManager(this);
}

class ProducerDaoManager {
  final _$ProducerDaoMixin _db;
  ProducerDaoManager(this._db);
  $$ProducersTableTableManager get producers =>
      $$ProducersTableTableManager(_db.attachedDatabase, _db.producers);
}

mixin _$ParcelDaoMixin on DatabaseAccessor<AppDatabase> {
  $ParcelsTable get parcels => attachedDatabase.parcels;
  ParcelDaoManager get managers => ParcelDaoManager(this);
}

class ParcelDaoManager {
  final _$ParcelDaoMixin _db;
  ParcelDaoManager(this._db);
  $$ParcelsTableTableManager get parcels =>
      $$ParcelsTableTableManager(_db.attachedDatabase, _db.parcels);
}

mixin _$SyncDaoMixin on DatabaseAccessor<AppDatabase> {
  $SyncQueueTable get syncQueue => attachedDatabase.syncQueue;
  $OutboxLogTable get outboxLog => attachedDatabase.outboxLog;
  SyncDaoManager get managers => SyncDaoManager(this);
}

class SyncDaoManager {
  final _$SyncDaoMixin _db;
  SyncDaoManager(this._db);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db.attachedDatabase, _db.syncQueue);
  $$OutboxLogTableTableManager get outboxLog =>
      $$OutboxLogTableTableManager(_db.attachedDatabase, _db.outboxLog);
}

mixin _$ReferenceDaoMixin on DatabaseAccessor<AppDatabase> {
  $ReferenceDataTable get referenceData => attachedDatabase.referenceData;
  ReferenceDaoManager get managers => ReferenceDaoManager(this);
}

class ReferenceDaoManager {
  final _$ReferenceDaoMixin _db;
  ReferenceDaoManager(this._db);
  $$ReferenceDataTableTableManager get referenceData =>
      $$ReferenceDataTableTableManager(_db.attachedDatabase, _db.referenceData);
}
