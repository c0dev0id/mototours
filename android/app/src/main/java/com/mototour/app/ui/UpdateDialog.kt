package com.mototour.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.mototour.app.data.UpdateInfo

@Composable
fun UpdateDialog(
    update: UpdateInfo,
    onInstall: () -> Unit,
    onDismiss: () -> Unit
) {
    var downloading by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = { if (!downloading) onDismiss() },
        title = { Text("Update Available") },
        text = {
            Column {
                Text("A new development build is available (${update.commitSha}).")
                if (update.body.isNotBlank()) {
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = update.body,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                }
                if (downloading) {
                    Spacer(Modifier.height(16.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp)
                        Spacer(Modifier.width(12.dp))
                        Text("Downloading…", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    downloading = true
                    onInstall()
                },
                enabled = !downloading
            ) {
                Text("Install")
            }
        },
        dismissButton = {
            TextButton(
                onClick = onDismiss,
                enabled = !downloading
            ) {
                Text("Skip")
            }
        }
    )
}
