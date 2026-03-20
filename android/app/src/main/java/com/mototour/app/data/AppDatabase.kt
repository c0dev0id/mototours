package com.mototour.app.data

import android.content.Context
import androidx.room.*
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(
    entities = [TourEntity::class, DayEntity::class, WaypointEntity::class],
    version = 2,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun tourDao(): TourDao

    companion object {
        @Volatile private var instance: AppDatabase? = null

        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE tours ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0")
                db.execSQL("ALTER TABLE tours ADD COLUMN completed_at INTEGER DEFAULT NULL")
            }
        }

        fun get(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "mototour.db"
                ).addMigrations(MIGRATION_1_2).build().also { instance = it }
            }
    }
}

class Converters {
    @TypeConverter fun fromCategory(c: TourCategory): String = c.name
    @TypeConverter fun toCategory(s: String): TourCategory = TourCategory.valueOf(s)
    @TypeConverter fun fromWaypointType(t: WaypointType): String = t.name
    @TypeConverter fun toWaypointType(s: String): WaypointType = WaypointType.valueOf(s)
}
