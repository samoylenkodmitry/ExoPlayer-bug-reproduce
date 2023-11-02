package com.example.myapplication

import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import fi.iki.elonen.NanoHTTPD
import java.io.IOException
import java.lang.Thread.sleep
import java.util.concurrent.atomic.AtomicLong

@UnstableApi
class MainActivity : AppCompatActivity() {

	override fun onCreate(savedInstanceState: Bundle?) {
		super.onCreate(savedInstanceState)
		setContentView(PlayerView(this).apply {
			controllerShowTimeoutMs = 100_000
			showController()
			player = ExoPlayer.Builder(context).build().apply {
				setMediaItem(MediaItem.fromUri("http://127.0.0.1:8080/gen/video.mp4"))
				prepare()
				playWhenReady = true
				val prev = AtomicLong()
				post(object : Runnable {
					override fun run() {
						val pos = contentPosition
						val delta = pos - prev.getAndSet(pos)
						if (delta > 500L) AlertDialog.Builder(context).setMessage("$delta ms skipped, pos=$pos").show()
						postDelayed(this, 100)
					}
				})
			}
		})
	}

	private val server = object : NanoHTTPD(8080) {

		override fun serve(session: IHTTPSession): Response = try {
			sleep(1337)
			newChunkedResponse(Response.Status.OK, "video/mp4", assets.open(session.uri.drop(1)))
		} catch (e: IOException) {
			newFixedLengthResponse(Response.Status.NOT_FOUND, MIME_PLAINTEXT, "File not found")
		}
	}.apply { start() }

	override fun onDestroy() {
		super.onDestroy()
		findViewById<PlayerView>(android.R.id.content).player?.release()
		server.stop()
	}
}