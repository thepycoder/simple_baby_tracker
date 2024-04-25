<!-- src/App.svelte -->
<script>
  import { db } from "./firebase";
  import {
    collection,
    addDoc,
    serverTimestamp,
    query,
    orderBy,
    onSnapshot,
    doc,
    updateDoc,
    limit,
    getDoc,
  } from "firebase/firestore";
  import { onMount, onDestroy } from "svelte";
  import { auth, googleProvider } from "./firebase";
  import { authState } from "rxfire/auth";
  import { signInWithPopup, signOut } from "firebase/auth";

  const db_table = "dev_entries";
  let foodType = "formula";
  let foodAmount = "200";
  let currentFoodDocId;
  let sleepStart, currentSleepDocId;
  let entries = [];
  let isSleeping = false;
  let isEating = false;
  let clockInterval;
  let sleepDuration = 0;
  let lastFoodStart, lastSleepEnd;
  let foodSinceLast = "N/A",
    sleepSinceLast = "N/A";
  let user = "";

  const unsubscribe = authState(auth).subscribe((u) => (user = u));

  function login() {
    signInWithPopup(auth, googleProvider);
  }

  function logout() {
    signOut();
  }

  // Functionality additions and modifications:
  function toggleFoodType(type) {
    console.log("Food Type: " + type);
    foodType = type;
  }

  // Enhanced local display functions
  function startFood() {
    const startTimestamp = serverTimestamp();
    isEating = true;
    addDoc(collection(db, db_table), {
      type: "food",
      subtype: foodType,
      start: startTimestamp,
      amount: foodAmount,
    }).then((docRef) => {
      currentFoodDocId = docRef.id;
      console.log("Added food " + foodType + startTimestamp + foodAmount);
    });
  }

  function endFood() {
    const endTimestamp = serverTimestamp();
    if (currentFoodDocId) {
      updateDoc(doc(db, db_table, currentFoodDocId), {
        amount: foodAmount,
        end: endTimestamp,
      }).then(() => {
        lastFoodStart = new Date();
        resetFood();
        updateFoodSinceLast();
      });
    }
  }

  function resetFood() {
    isEating = false;
    foodType = "formula";
    foodAmount = "200";
  }

  function formatTime(microseconds) {
    const seconds = microseconds / 1000;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.round(seconds % 60);

    // Creating a padded string for minutes and seconds for uniformity
    const paddedMinutes = String(minutes).padStart(2, "0");
    const paddedSeconds = String(remainingSeconds).padStart(2, "0");

    // Creating the final formatted string
    return `${hours}:${paddedMinutes}:${paddedSeconds}`;
  }

  function formatCardTime(start, end) {
    // Create a Date object from the start timestamp
    const startDate = new Date(start);
    // Format the start date and time
    const startDay = startDate.getDate().toString().padStart(2, "0");
    const startMonth = (startDate.getMonth() + 1).toString().padStart(2, "0");
    const startHour = startDate.getHours().toString().padStart(2, "0");
    const startMinute = startDate.getMinutes().toString().padStart(2, "0");
    const formattedStart = `${startDay}/${startMonth}: ${startHour}:${startMinute}`;

    // Check if the end timestamp is not null
    if (end !== null) {
      // Create a Date object from the end timestamp
      const endDate = new Date(end);
      // Format the end time
      const endHour = endDate.getHours().toString().padStart(2, "0");
      const endMinute = endDate.getMinutes().toString().padStart(2, "0");
      const formattedEnd = `${endHour}:${endMinute}`;

      // Return the full date range string
      return `${formattedStart} - ${formattedEnd}`;
    } else {
      // Return the string with "nog bezig"
      return `${formattedStart} - nog bezig`;
    }
  }

  function startSleep() {
    const startTimestamp = serverTimestamp();
    sleepStart = new Date();
    isSleeping = true;
    addDoc(collection(db, db_table), {
      type: "sleep",
      start: startTimestamp,
    }).then((docRef) => {
      currentSleepDocId = docRef.id;
      startClock();
    });
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    if (currentSleepDocId) {
      updateDoc(doc(db, db_table, currentSleepDocId), {
        end: endTimestamp,
      }).then(() => {
        lastSleepEnd = new Date();
        resetSleep();
        updateSleepSinceLast();
      });
    }
  }

  function updateFoodSinceLast() {
    if (lastFoodStart) {
      const interval = setInterval(() => {
        const now = new Date();
        foodSinceLast = formatTime(now - lastFoodStart);
      }, 1000);
      // onDestroy(() => clearInterval(interval));
    }
  }

  function updateSleepSinceLast() {
    if (lastSleepEnd) {
      const interval = setInterval(() => {
        const now = new Date();
        sleepSinceLast = formatTime(now - lastSleepEnd);
      }, 1000);
      // onDestroy(() => clearInterval(interval));
    }
  }

  function resetSleep() {
    isSleeping = false;
    stopClock();
  }

  // Clock logic remains similar
  function startClock() {
    clearInterval(clockInterval);
    clockInterval = setInterval(updateSleepDuration, 1000);
  }

  function updateSleepDuration() {
    if (isSleeping) {
      const now = new Date();
      const elapsed = now - sleepStart;
      sleepDuration = Math.floor(elapsed);
    }
  }

  function stopClock() {
    clearInterval(clockInterval);
    sleepDuration = 0;
  }

  onMount(() => {
    const q = query(
      collection(db, db_table),
      orderBy("start", "desc"),
      limit(10)
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      entries = snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          id: doc.id,
          ...data,
          start: data.start.toDate(),
          end: data.end ? data.end.toDate() : null,
        };
      });
      // Initialize latest end times
      const lastSleep = entries.find((e) => e.type === "sleep" && e.end);
      const lastFood = entries.find((e) => e.type === "food" && e.start);

      if (lastSleep) {
        lastSleepEnd = lastSleep.end;
        updateSleepSinceLast();
      }
      if (lastFood) {
        lastFoodStart = lastFood.start;
        updateFoodSinceLast();
      }
      // Update current activity states based on the latest entries
      updateCurrentActivities();
    });
    return () => unsubscribe();
  });

  function increaseAmount() {
    foodAmount = (+foodAmount + 10).toString(); // Convert to number, increment, and back to string to handle binding correctly
  }

  function decreaseAmount() {
    if (foodAmount > 10) {
      // Ensure the amount doesn't go negative
      foodAmount = (+foodAmount - 10).toString();
    }
  }

  function updateCurrentActivities() {
    let activeSleepEntry = entries.find(
      (entry) => entry.type === "sleep" && !entry.end
    );
    let activeFoodEntry = entries.find(
      (entry) => entry.type === "food" && !entry.end
    );

    if (activeSleepEntry) {
      currentSleepDocId = activeSleepEntry.id;
      sleepStart = activeSleepEntry.start;
      if (!isSleeping) {
        isSleeping = true;
        startClock();
      }
    } else if (isSleeping) {
      isSleeping = false;
      stopClock();
    }

    isEating = !!activeFoodEntry;
    if (activeFoodEntry) {
      currentFoodDocId = activeFoodEntry.id;
    }
  }

  function isLatestEntry(entry, type) {
    const latestEntry = entries.find((e) => e.type === type && !e.end);
    return latestEntry && latestEntry.id === entry.id;
  }
</script>

<main class="container mt-5">
  {#if user}
    <h1 class="text-center mb-4">Lio's Activities Tracker</h1>
    <div class="row justify-content-center">
      <section class="col-md-6 mb-3">
        <p class="text-muted text-center mt-2">
          Time since last sleep: {sleepSinceLast}
        </p>
        <button
          on:click={startSleep}
          class="btn btn-primary w-100"
          disabled={isSleeping}>Start Sleep</button
        >
        {#if isSleeping}
          <button on:click={endSleep} class="btn btn-danger w-100 mt-2"
            >Stop Sleep</button
          >
          <p class="text-muted text-center mt-2">
            Lio has been sleeping for {formatTime(sleepDuration)}.
          </p>
        {/if}
      </section>
      <section class="col-md-6 mb-3">
        <p class="text-muted text-center mt-2">
          Time since last food: {foodSinceLast}
        </p>
        <button
          on:click={startFood}
          class="btn btn-primary w-100"
          disabled={isEating}
        >
          Start Food Entry
        </button>
        {#if isEating}
          <div class="btn-group mt-2 w-100">
            <button
              on:click={() => toggleFoodType("formula")}
              class={foodType === "formula"
                ? "btn btn-danger"
                : "btn btn-outline-danger"}
            >
              <i class="bi bi-cup-straw"></i> Infant Formula
            </button>
            <button
              on:click={() => toggleFoodType("solid")}
              class={foodType === "solid"
                ? "btn btn-success"
                : "btn btn-outline-success"}
            >
              <i class="bi bi-apple"></i> Solid Food
            </button>
          </div>
          <div class="input-group mt-2">
            <button
              class="btn btn-outline-secondary"
              type="button"
              on:click={decreaseAmount}>-10</button
            >
            <input
              type="number"
              bind:value={foodAmount}
              class="form-control"
              placeholder="Hoeveel?"
            />
            <button
              class="btn btn-outline-secondary"
              type="button"
              on:click={increaseAmount}>+10</button
            >
          </div>
          <button on:click={endFood} class="btn btn-success w-100 mt-2">
            Log Food Entry
          </button>
        {/if}
      </section>
    </div>
    <div class="row justify-content-center">
      <div class="col-md-6">
        <h3 class="text-center mb-3">Sleep Entries</h3>
        {#each entries.filter((e) => e.type === "sleep") as entry}
          <div
            class={isLatestEntry(entry, "sleep")
              ? "card mb-3 border-info"
              : "card mb-3"}
          >
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-moon-stars"></i> Sleep
              </h5>
              <p class="card-text">{formatCardTime(entry.start, entry.end)}</p>
              <p class="card-text">
                Duration: {entry.end
                  ? formatTime(entry.end - entry.start)
                  : "In progress"}
              </p>
            </div>
          </div>
        {/each}
      </div>
      <div class="col-md-6">
        <h3 class="text-center mb-3">Food Entries</h3>
        {#each entries.filter((e) => e.type === "food") as entry}
          <div
            class={isLatestEntry(entry, "food")
              ? "card mb-3 border-warning"
              : "card mb-3"}
          >
            <div class="card-body">
              <h5 class="card-title">
                <i
                  class={entry.subtype === "formula"
                    ? "bi bi-cup-straw"
                    : "bi bi-apple"}
                ></i>
                {entry.end
                  ? entry.subtype === "formula"
                    ? "Infant Formula"
                    : "Solid Food"
                  : "Nog bezig"}
              </h5>
              <p class="card-text">{formatCardTime(entry.start, entry.end)}</p>
              <p class="card-text">
                Amount: {entry.amount ? entry.amount + " ml" : "Niet ingevuld"}
              </p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="headerBar">
      <h1 class="header top">Victor's baby tracker!</h1>
      <button on:click={login} class="btn btn-primary"
        >Sign in with google</button
      >
    </div>
  {/if}
</main>

<style>
  :global(.isSleeping) {
    background-color: #e3f2fd; /* Light blue */
  }
  :global(.isEating) {
    background-color: #e8f5e9; /* Light green */
  }
</style>
