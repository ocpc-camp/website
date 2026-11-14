/**
 * Self-contained Discord invite widget
 * Fetches server info and displays an invitation banner.
 *
 * Caches the invite response in localStorage (stale-while-revalidate): the card
 * paints instantly from cache on every load — so navigating between sites (e.g.
 * the Hong Kong / Iași toggle) doesn't flash a blank box — and the network is
 * only hit when the cache is missing or older than CACHE_TTL, refreshing the
 * live member/online counts in the background.
 */
(function() {
  'use strict';

  const DISCORD_API_BASE = 'https://discord.com/api/v10';
  const CACHE_TTL = 10 * 60 * 1000; // ms — how long a cached response counts as "fresh"
  const cacheKey = (code) => 'ocpcDiscordInvite:' + code;

  function readCache(inviteCode) {
    try {
      const raw = localStorage.getItem(cacheKey(inviteCode));
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && parsed.data ? parsed : null; // { data, ts }
    } catch (e) {
      return null; // localStorage unavailable (e.g. private mode) — fall back to network
    }
  }

  function writeCache(inviteCode, data) {
    try {
      localStorage.setItem(cacheKey(inviteCode), JSON.stringify({ data: data, ts: Date.now() }));
    } catch (e) { /* ignore quota / disabled storage */ }
  }

  /**
   * Initialize Discord invite widgets on the page
   * @param {string} inviteCode - Discord invite code
   */
  window.initDiscordInvite = function(inviteCode) {
    if (!inviteCode) {
      console.error('Discord invite code is required');
      return;
    }

    const containers = document.querySelectorAll('[data-discord-invite]');
    if (!containers.length) return;

    const cached = readCache(inviteCode);

    // 1) Paint immediately from cache so switching pages doesn't flash a blank box.
    if (cached) {
      containers.forEach(container => renderInvite(container, cached.data, inviteCode));
    }

    // 2) Hit the network only if we have no cache or it's stale (stale-while-revalidate).
    const isFresh = cached && (Date.now() - cached.ts) < CACHE_TTL;
    if (!isFresh) {
      fetchInviteData(inviteCode)
        .then(data => {
          writeCache(inviteCode, data);
          containers.forEach(container => renderInvite(container, data, inviteCode));
        })
        .catch(error => {
          // Only surface an error if we had nothing cached to show.
          if (!cached) containers.forEach(container => renderError(container, error));
          else console.error('Discord invite refresh failed:', error);
        });
    }
  };

  /**
   * Fetch Discord invite data from API
   */
  function fetchInviteData(inviteCode) {
    return fetch(`${DISCORD_API_BASE}/invites/${inviteCode}?with_counts=true`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch invite data');
        }
        return response.json();
      });
  }

  /**
   * Render the Discord invite widget
   */
  function renderInvite(container, data, inviteCode) {
    const serverName = data.guild.name;
    const memberCount = data.approximate_member_count?.toLocaleString() || '0';
    const onlineCount = data.approximate_presence_count?.toLocaleString() || '0';
    const iconUrl = data.guild.icon
      ? `https://cdn.discordapp.com/icons/${data.guild.id}/${data.guild.icon}.png?size=128`
      : null;
    const inviteUrl = `https://discord.gg/${inviteCode}`;

    container.innerHTML = `
      <div class="discord-invite-card">
        <div class="discord-invite-header">
          <div class="discord-invite-icon-wrapper">
            ${iconUrl
              ? `<img src="${iconUrl}" alt="${serverName}" class="discord-invite-icon">`
              : `<div class="discord-invite-icon discord-invite-icon-placeholder">${serverName.charAt(0)}</div>`
            }
          </div>
          <div class="discord-invite-info">
            <div class="discord-invite-server-name">${serverName}</div>
            <div class="discord-invite-stats">
              <span class="discord-invite-stat">
                <span class="discord-invite-status-dot discord-online"></span>
                <span class="discord-invite-stat-text">${onlineCount} online</span>
              </span>
              <span class="discord-invite-stat">
                <span class="discord-invite-status-dot discord-offline"></span>
                <span class="discord-invite-stat-text">${memberCount} members</span>
              </span>
            </div>
          </div>
        </div>
        <a href="${inviteUrl}" target="_blank" rel="noopener noreferrer" class="discord-invite-button">
          Join Server
        </a>
      </div>
    `;
  }

  /**
   * Render error state
   */
  function renderError(container, error) {
    console.error('Discord invite error:', error);
    container.innerHTML = `
      <div class="alert alert-warning" role="alert">
        Unable to load Discord invite. Please try again later.
      </div>
    `;
  }
})();
