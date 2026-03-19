package com.mototour.app.ui

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.mototour.app.ui.detail.TourDetailScreen
import com.mototour.app.ui.map.MapScreen
import com.mototour.app.ui.pdf.PdfScreen
import com.mototour.app.ui.tourlist.TourListScreen

object Routes {
    const val TOUR_LIST = "tours"
    const val TOUR_DETAIL = "tour/{tourId}"
    const val MAP = "map/{dayId}"
    const val PDF = "pdf/{tourId}"

    fun tourDetail(tourId: Long) = "tour/$tourId"
    fun map(dayId: Long) = "map/$dayId"
    fun pdf(tourId: Long) = "pdf/$tourId"
}

@Composable
fun MotoTourNavHost() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.TOUR_LIST) {

        composable(Routes.TOUR_LIST) {
            TourListScreen(
                onTourClick = { tourId -> navController.navigate(Routes.tourDetail(tourId)) }
            )
        }

        composable(
            Routes.TOUR_DETAIL,
            arguments = listOf(navArgument("tourId") { type = NavType.LongType })
        ) { entry ->
            val tourId = entry.arguments!!.getLong("tourId")
            TourDetailScreen(
                tourId = tourId,
                onDayMapClick = { dayId -> navController.navigate(Routes.map(dayId)) },
                onPdfClick = { navController.navigate(Routes.pdf(tourId)) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            Routes.MAP,
            arguments = listOf(navArgument("dayId") { type = NavType.LongType })
        ) { entry ->
            val dayId = entry.arguments!!.getLong("dayId")
            MapScreen(
                dayId = dayId,
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            Routes.PDF,
            arguments = listOf(navArgument("tourId") { type = NavType.LongType })
        ) { entry ->
            val tourId = entry.arguments!!.getLong("tourId")
            PdfScreen(
                tourId = tourId,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
