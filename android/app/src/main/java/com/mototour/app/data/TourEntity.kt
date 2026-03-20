package com.mototour.app.data

import androidx.room.*

enum class TourCategory {
    DAY, WEEKEND, THREE_DAY, SIX_DAY;

    val label: String get() = when (this) {
        DAY -> "Day Tours"
        WEEKEND -> "Weekend Tours"
        THREE_DAY -> "3-Day Tours"
        SIX_DAY -> "6-Day Tours"
    }
}

@Entity(tableName = "tours")
data class TourEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val slug: String,
    val category: TourCategory,
    val region: String,
    @ColumnInfo(name = "total_distance_km") val totalDistanceKm: Int,
    @ColumnInfo(name = "day_count") val dayCount: Int,
    val overview: String,
    val highlights: String,
    @ColumnInfo(name = "road_character") val roadCharacter: String,
    @ColumnInfo(name = "pdf_path") val pdfPath: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "is_favorite", defaultValue = "0") val isFavorite: Boolean = false,
    @ColumnInfo(name = "completed_at", defaultValue = "NULL") val completedAt: Long? = null
)

@Entity(
    tableName = "days",
    foreignKeys = [ForeignKey(
        entity = TourEntity::class,
        parentColumns = ["id"],
        childColumns = ["tour_id"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("tour_id")]
)
data class DayEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "tour_id") val tourId: Long,
    @ColumnInfo(name = "day_number") val dayNumber: Int,
    val name: String,
    @ColumnInfo(name = "distance_km") val distanceKm: Int,
    val description: String,
    @ColumnInfo(name = "gpx_path") val gpxPath: String
)

@Entity(
    tableName = "waypoints",
    foreignKeys = [ForeignKey(
        entity = DayEntity::class,
        parentColumns = ["id"],
        childColumns = ["day_id"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("day_id")]
)
data class WaypointEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "day_id") val dayId: Long,
    @ColumnInfo(name = "order_index") val orderIndex: Int,
    val name: String,
    val lat: Double,
    val lon: Double,
    val description: String,
    val type: WaypointType
)

enum class WaypointType {
    START, END, VIA, MIDPOINT, OVERNIGHT
}

/** Tour with all its days, for list/detail display. */
data class TourWithDays(
    @Embedded val tour: TourEntity,
    @Relation(parentColumn = "id", entityColumn = "tour_id")
    val days: List<DayEntity>
)

/** Day with its waypoints, for map display. */
data class DayWithWaypoints(
    @Embedded val day: DayEntity,
    @Relation(parentColumn = "id", entityColumn = "day_id")
    val waypoints: List<WaypointEntity>
)
