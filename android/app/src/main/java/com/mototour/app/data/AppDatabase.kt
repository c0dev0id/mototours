package com.mototour.app.data

import android.content.Context
import androidx.room.*

@Database(
    entities = [TourEntity::class, DayEntity::class, WaypointEntity::class],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun tourDao(): TourDao

    companion object {
        @Volatile private var instance: AppDatabase? = null

        fun get(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "mototour.db"
                ).build().also { instance = it }
            }
    }
}

class Converters {
    @TypeConverter fun fromCategory(c: TourCategory): String = c.name
    @TypeConverter fun toCategory(s: String): TourCategory = TourCategory.valueOf(s)
    @TypeConverter fun fromWaypointType(t: WaypointType): String = t.name
    @TypeConverter fun toWaypointType(s: String): WaypointType = WaypointType.valueOf(s)
}
