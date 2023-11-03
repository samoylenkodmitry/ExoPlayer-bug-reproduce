# Minimal Project to Reproduce the ExoPlayer Skip Bug

https://github.com/androidx/media/issues/786

## TL;DR

ExoPlayer occasionally skips several seconds' worth of frames when playing a video from a remote server.

## ExoPlayer Version


```
media3-exoplayer = "1.1.1" (and at least 2 previous)
```

## Steps to Reproduce

1. Create an Android emulator with API 30, x86, or x86_64 ABI, Android 11.0 (Google APIs or Google Play).
2. Run the application on the emulator.
3. Close the application after playback finishes.
4. Run the application again (repeat if necessary).

## Expected Result

The video should start playing from the beginning and play through to the end without issues.

## Actual Result

The video starts from the beginning but then skips some frames at a certain point in the middle of the playback.

## Notes

- The bug cannot be replicated on any other emulator versions (API 28, 29, 31, 32, 33, 34) or is hard to replicate.
- The bug cannot be replicated on a physical device (Samsung Galaxy SM-G970, Android 13), or is hard to replicate.
- The bug is not present when playing from a local asset or when there is no network delay.
- The bug has been reproduced while playing a single `mp4` file as well as while playing a `dash` stream composed of `mp4` chunks.

## Video

To replicate the bug, use the script `python gen_mp4.py` found in `app/src/main/assets/gen`. 
The script requires `ffmpeg` to be installed.
The video is composed of several chunks concatenated together, with each chunk being a 3-second video displaying a random color.

## Code to reproduce the bug

### Dependencies
```toml
[versions]
agp = "8.3.0-alpha11"
kotlin = "1.9.0"
core-ktx = "1.12.0"
media3-common = "1.1.1"
media3-exoplayer = "1.1.1"
media3-ui = "1.1.1"
media3-exoplayer-dash = "1.1.1"
nanohttpd = "2.3.1"

[libraries]
core-ktx = { group = "androidx.core", name = "core-ktx", version.ref = "core-ktx" }
androidx-media3-common = { group = "androidx.media3", name = "media3-common", version.ref = "media3-common" }
androidx-media3-exoplayer = { group = "androidx.media3", name = "media3-exoplayer", version.ref = "media3-exoplayer" }
androidx-media3-ui = { group = "androidx.media3", name = "media3-ui", version.ref = "media3-ui" }
androidx-media3-dash = { group = "androidx.media3", name = "media3-exoplayer-dash", version.ref = "media3-exoplayer-dash" }
nanohttpd = { group = "org.nanohttpd", name = "nanohttpd", version.ref = "nanohttpd" }

[plugins]
androidApplication = { id = "com.android.application", version.ref = "agp" }
kotlinAndroid = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }

```
### Activity

```kotlin
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
}
```
