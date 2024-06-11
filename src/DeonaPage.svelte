<script>
  import { foodEntries, sleepEntries } from "./stores";
  import { formatForCopy } from "./utils";
  import { writable } from "svelte/store";

  let isLoading = writable(false);
  let errorMessage = writable("");
  let responseData = writable(null);

  async function makeApiRequest() {
    errorMessage.set("");
    responseData.set(null);
    isLoading.set(true);

    try {
      const response = await fetch(
        "https://update-from-deona-dbx5pfpliq-ew.a.run.app",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.text();
        console.log(data);
        responseData.set(data);
      } else if (response.status === 400) {
        const errorText = await response.text();
        errorMessage.set(errorText);
      } else {
        errorMessage.set("An unknown error occurred");
      }
    } catch (error) {
      console.log(error);
      errorMessage.set("Network error");
    } finally {
      isLoading.set(false);
    }
  }

  let inputText = "";
  let sleepEnd;
  if ($sleepEntries[0] && $sleepEntries[0].end) {
    sleepEnd = $sleepEntries[0].end;
  } else {
    // If no end, just take right now
    sleepEnd = new Date();
  }
  if ($foodEntries[0] && $sleepEntries[0]) {
    inputText = `Lio heeft geslapen tot ${formatForCopy(sleepEnd)} en laatst gegeten om ${formatForCopy($foodEntries[0].start)}`;
  }

  console.log($foodEntries[0]);

  function copyToClipboard() {
    navigator.clipboard.writeText(inputText);
  }

  function sync() {
    alert("Syncing...");
  }
</script>

<div class="container">
  <div class="row mb-2 mt-4 justify-content-center">
    <div class="col-lg-8">
      {#if $errorMessage}
        <div class="alert alert-danger mt-2">
          Error: {$errorMessage}
        </div>
      {/if}

      {#if $responseData}
        <div class="alert alert-success mt-2">
          Response: {$responseData}
        </div>
      {/if}
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col">
              <textarea
                type="text"
                class="form-control mb-2"
                rows="8"
                bind:value={inputText}
              />
              <button class="btn btn-primary w-100" on:click={copyToClipboard}>
                Copy to Clipboard
              </button>
            </div>
            <div class="col">
              <button
                class="btn btn-primary w-100 h-100"
                on:click={makeApiRequest}
                disabled={$isLoading}
              >
                Sync
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
