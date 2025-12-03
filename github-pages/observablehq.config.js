export default {
  title: "OHDSI-Stroke",
  pages: [
    { name: "Home", path: "/" },
    { name: "Methodology", path: "/methodology" },
    { name: "Interactive Cohort Explorer", path: "/cohort-explorer" },
    { name: "Statistics Report", path: "/statistics-report" },
    { name: "Predictive Modeling Report", path: "/predictive-modeling" },
    { name: "Explanatory Modeling Report", path: "/explanatory-modeling" },
    { name: "Visualizations", path: "/visualizations" },
    { name: "Key Takeaways", path: "/key-takeaways" },
    { name: "Conclusions", path: "/conclusions" },
  ],
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32">',
  root: "src",
  output: "dist",
  cleanUrls: true,
};
