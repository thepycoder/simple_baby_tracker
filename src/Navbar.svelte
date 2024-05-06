<!-- src/Navbar.svelte -->
<script>
  import { link } from "svelte-routing";
</script>

<nav class="navbar navbar-expand navbar-light bg-light">
  <div class="container">
    <div class="navbar-brand"></div>
    <div class="navbar-nav">
      <a class="nav-item nav-link" use:link href="/"
        ><button type="button" class="btn btn-outline-secondary">Timers</button
        ></a
      >
      <a class="nav-item nav-link" use:link href="/stats"
        ><button type="button" class="btn btn-outline-secondary">Stats</button
        ></a
      >
      <a class="nav-item nav-link" use:link href="/deona"
        ><button type="button" class="btn btn-outline-secondary">Deona</button
        ></a
      >
    </div>
  </div>
</nav>
