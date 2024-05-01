<script>
  import { writable, get } from "svelte/store";
  import { formatTime, convertToDatetimeLocal } from "./utils";
  import { db, db_table } from "./firebase";
  import {
    updateDoc,
    doc,
    serverTimestamp,
    query,
    collection,
    orderBy,
    limit,
    onSnapshot,
    addDoc,
    where,
  } from "firebase/firestore";
  import { foodEntries } from "./stores";

  const isEating = writable(false);
  const foodType = writable("formula");
  const foodAmount = writable("200");
  const eatDuration = writable(0);
  const clockFoodInterval = writable(null);
  const foodStart = writable(null);
  const currentFoodDocId = writable(null);
  const lastFoodStart = writable(null);
  const foodSinceLast = writable("N/A");

  function resetFood() {
    isEating.set(false);
    foodType.set("formula");
    foodAmount.set("200");
    stopFoodClock();
  }

  function startFoodClock() {
    clearInterval(get(clockFoodInterval));
    clockFoodInterval.set(setInterval(updateFoodDuration, 1000));
  }

  function updateFoodDuration() {
    if (get(isEating)) {
      const now = new Date();
      const elapsed = now - get(foodStart);
      eatDuration.set(Math.floor(elapsed));
    }
  }

  // Functionality additions and modifications:
  function toggleFoodType(type) {
    foodType.set(type);
  }

  // Enhanced local display functions
  function startFood() {
    const startTimestamp = serverTimestamp();
    foodStart.set(new Date());
    isEating.set(true);
    addDoc(collection(db, db_table), {
      type: "food",
      subtype: get(foodType),
      start: startTimestamp,
      amount: get(foodAmount),
    }).then((docRef) => {
      currentFoodDocId.set(docRef.id);
      startFoodClock();
    });
  }

  function endFood() {
    const endTimestamp = serverTimestamp();
    if (get(currentFoodDocId)) {
      updateDoc(doc(db, db_table, get(currentFoodDocId)), {
        amount: get(foodAmount),
        end: endTimestamp,
      }).then(() => {
        lastFoodStart.set(new Date());
        resetFood();
        updateFoodSinceLast();
      });
    }
  }

  function updateFoodSinceLast() {
    const interval = setInterval(() => {
      const now = new Date();
      foodSinceLast.set(formatTime(now - get(lastFoodStart)));
    }, 1000);
  }

  function stopFoodClock() {
    clearInterval(get(clockFoodInterval));
  }

  function increaseAmount() {
    foodAmount.set((+get(foodAmount) + 10).toString()); // Convert to number, increment, and back to string to handle binding correctly
  }

  function decreaseAmount() {
    if (get(foodAmount) > 10) {
      // Ensure the amount doesn't go negative
      foodAmount.set((+get(foodAmount) - 10).toString());
    }
  }

  $: $foodEntries, init();

  function init() {
    // Initialize latest end times
    const lastFood = $foodEntries[0];

    if (lastFood) {
      isEating.set(!Boolean(lastFood.end));
      if (lastFood.end) {
        lastFoodStart.set(lastFood.start);
        updateFoodSinceLast();
      } else {
        currentFoodDocId.set(lastFood.id);
        foodStart.set(lastFood.start);
        startFoodClock();
      }
    }
  }
</script>

{#if $isEating}
  <p class="text-muted text-center mt-2">
    Aan het eten voor: <b class="fs-2">{formatTime($eatDuration)}</b>
  </p>
  <div class="btn-group mt-2 w-100">
    <button
      on:click={() => toggleFoodType("formula")}
      class={$foodType === "formula"
        ? "btn btn-primary"
        : "btn btn-outline-primary"}
      ><i class="bi bi-cup-straw"></i> Infant Formula
    </button>
    <button
      on:click={() => toggleFoodType("solid")}
      class={$foodType === "solid"
        ? "btn btn-success"
        : "btn btn-outline-success"}
      ><i class="bi bi-apple"></i> Solid Food
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
      bind:value={$foodAmount}
      class="form-control"
      placeholder="Hoeveel?"
    />
    <button
      class="btn btn-outline-secondary"
      type="button"
      on:click={increaseAmount}>+10</button
    >
  </div>
  <button on:click={endFood} class="btn btn-danger w-100 mt-2">Stop eten</button
  >
{:else}
  <p class="text-muted text-center mt-2">
    Tijd sinds laatste maaltijd: <b class="fs-2">{$foodSinceLast}</b>
  </p>
  <button
    on:click={startFood}
    class="btn btn-primary w-100 mt-2"
    disabled={$isEating}>Start Eten</button
  >
{/if}
