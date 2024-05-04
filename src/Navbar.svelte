<!-- src/Navbar.svelte -->
<script>
  import { link } from "svelte-routing";
</script>

<nav class="navbar navbar-expand navbar-light bg-light fixed-top">
  <div class="container">
    <div class="navbar-nav">
      <a class="nav-item nav-link" use:link href="/">Timers</a>
      <a class="nav-item nav-link" use:link href="/stats">Stats</a>
    </div>
  </div>
</nav>
