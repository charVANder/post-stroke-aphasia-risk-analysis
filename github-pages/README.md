
```bash
# Install dependencies
npm install

# Start development server from inside the github-pages directory
npm run dev
```

`http://localhost:3000` to view

## Build & Deploy

```bash
# Build for production
npm run build
```

The built site will be in the `dist/` directory.

### GitHub Pages Deployment
for future
1. Run `npm run build`
2. Push the `dist/` folder to your repository
3. In GitHub repository settings, go to Pages
4. Set source to deploy from branch, select the branch/folder containing `dist/`

Or use GitHub Actions for automatic deployment.

## TODO

- Add more visualizations
- Enhance styling
- Add filtering controls
