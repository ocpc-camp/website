/**
 * Self-contained Discord invite widget
 * Fetches server info and displays an invitation banner
 */
(function() {
  'use strict';

  const DISCORD_API_BASE = 'https://discord.com/api/v10';
  
  /**
   * Initialize Discord invite widgets on the page
   * @param {string} inviteCode - Discord invite code
   */
  window.initDiscordInvite = function(inviteCode) {
    if (!inviteCode) {
      console.error('Discord invite code is required');
      return;
    }

    // Find all Discord invite containers
    const containers = document.querySelectorAll('[data-discord-invite]');
    
    containers.forEach(container => {
      fetchInviteData(inviteCode)
        .then(data => renderInvite(container, data, inviteCode))
        .catch(error => renderError(container, error));
    });
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
