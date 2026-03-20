package com.mototour.app.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface TourDao {

    @Transaction
    @Query("SELECT * FROM tours ORDER BY category, name")
    fun allToursWithDays(): Flow<List<TourWithDays>>

    @Transaction
    @Query("SELECT * FROM tours WHERE category = :category ORDER BY name")
    fun toursByCategory(category: TourCategory): Flow<List<TourWithDays>>

    @Transaction
    @Query("SELECT * FROM tours WHERE id = :id")
    suspend fun tourWithDays(id: Long): TourWithDays?

    @Transaction
    @Query("SELECT * FROM days WHERE id = :dayId")
    suspend fun dayWithWaypoints(dayId: Long): DayWithWaypoints?

    @Transaction
    @Query("SELECT * FROM days WHERE tour_id = :tourId ORDER BY day_number")
    suspend fun daysWithWaypoints(tourId: Long): List<DayWithWaypoints>

    @Insert
    suspend fun insertTour(tour: TourEntity): Long

    @Insert
    suspend fun insertDay(day: DayEntity): Long

    @Insert
    suspend fun insertWaypoints(waypoints: List<WaypointEntity>)

    @Delete
    suspend fun deleteTour(tour: TourEntity)

    @Query("SELECT COUNT(*) FROM tours")
    suspend fun tourCount(): Int

    @Query("SELECT EXISTS(SELECT 1 FROM tours WHERE slug = :slug AND category = :category)")
    suspend fun tourExists(slug: String, category: TourCategory): Boolean

    @Query("UPDATE tours SET is_favorite = :favorite WHERE id = :tourId")
    suspend fun setFavorite(tourId: Long, favorite: Boolean)

    @Query("UPDATE tours SET completed_at = :completedAt WHERE id = :tourId")
    suspend fun setCompletedAt(tourId: Long, completedAt: Long?)
}
