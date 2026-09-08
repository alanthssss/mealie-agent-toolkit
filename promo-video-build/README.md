# Launch video source

Editable Remotion 4 source for the 18-second vertical launch video.

```bash
npm install
npm run lint
npx remotion render MyComp ../promo/video/out/mealie-quality-operator-vertical.mp4 --codec=h264
```

The composition is 1080×1920 at 30 fps and uses only repository-owned visual assets. The generated MP4 is checked in so publishers do not need Node or Remotion.
