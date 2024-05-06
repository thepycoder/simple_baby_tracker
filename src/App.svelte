<!-- src/App.svelte -->
<script>
  import { Router, Route } from "svelte-routing";
  import { authState } from "rxfire/auth";
  import { auth, googleProvider } from "./firebase";
  import { signInWithPopup, signOut } from "firebase/auth";
  import Navbar from "./Navbar.svelte";
  import TimerPage from "./TimerPage.svelte";
  import StatsPage from "./StatsPage.svelte";
  import DeonaPage from "./DeonaPage.svelte";

  let user = null;

  // Subscribe to auth state changes
  const unsubscribe = authState(auth).subscribe((u) => {
    user = u;
  });

  function login() {
    signInWithPopup(auth, googleProvider);
  }

  function logout() {
    signOut(auth);
  }
</script>

{#if user}
  <Navbar {logout} />
  <Router>
    <Route path="/" component={TimerPage} />
    <Route path="/stats" component={StatsPage} />
    <Route path="/deona" component={DeonaPage} />
  </Router>
{:else}
  <div class="headerBar">
    <h1 class="header top">Victor's baby tracker!</h1>
    <button on:click={login} class="btn btn-primary">Sign in with Google</button
    >
  </div>
{/if}
