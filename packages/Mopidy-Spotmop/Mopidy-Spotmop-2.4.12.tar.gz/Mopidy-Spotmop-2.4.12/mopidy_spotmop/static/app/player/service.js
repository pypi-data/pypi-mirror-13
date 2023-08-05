/**
 * Create a Player service
 *
 * This holds all of the calls for the player interface and data
 **/
 
angular.module('spotmop.services.player', [])

.factory("PlayerService", ['$rootScope', '$interval', 'SettingsService', 'MopidyService', 'SpotifyService', 'EchonestService', 'NotifyService', function( $rootScope, $interval, SettingsService, MopidyService, SpotifyService, EchonestService, NotifyService ){
	
	// setup initial states
	var state = {
		playing: false,
		isRepeat: false,
		isRandom: false,
		isMute: false,
		volume: 100,
		playPosition: 0,
		currentTlTrack: false,
		playPositionPercent: function(){
			if( state.currentTlTrack ){
				return ( state.playPosition / state.currentTlTrack.track.length * 100 ).toFixed(2);
			}else{
				return 0;
			}
		}
	}
	
	// when mopidy connection detected, fetch real states
	$rootScope.$on('mopidy:state:online', function(){
		updateToggles();
		
		updateCurrentTrack();
		updatePlayerState();
		updateVolume();
		
		// figure out if we're playing already
		MopidyService.getState().then( function( newState ){
			if( newState == 'playing' )
				state.playing = true;
			else
				state.playing = false;
		});
	});
	
	// listen for changes from other clients
	$rootScope.$on('mopidy:event:optionsChanged', function(event, options){
		updateToggles();
	});
	
	$rootScope.$on('mopidy:event:playbackStateChanged', function( event, state ){
		updatePlayerState( state.new_state );
	});
	
	$rootScope.$on('mopidy:event:seeked', function( event, position ){
		updatePlayPosition( position.time_position );
	});
	
	$rootScope.$on('mopidy:event:volumeChanged', function( event, volume ){
		if( volume.volume != state.volume )
			updateVolume( volume.volume );
	});
	
	
	// update our toggle states from the mopidy server
	function updateToggles(){	
        MopidyService.getRepeat().then( function(isRepeat){
            state.isRepeat = isRepeat;
        });
        MopidyService.getRandom().then( function(isRandom){
            state.isRandom = isRandom;
        });
        MopidyService.getMute().then( function(isMute){
            state.isMute = isMute;
        });
	}
	
	// listen for current track changes
	// TODO: Move this into the MopidyService for sanity
	$rootScope.$on('mopidy:event:trackPlaybackStarted', function( event, tlTrack ){
		state.currentTlTrack = tlTrack.tl_track;		
		updateCurrentTrack( tlTrack.tl_track );
		updatePlayerState();
	});
	
	
	/**
	 * Set the new play position and, if required, figure it out first
	 * @param newPosition = integer (optional)
	 **/
	function updatePlayPosition( newPosition ){
	
		// if we haven't been provided with a specific new position
		if( typeof( newPosition ) === 'undefined' ){
		
			// go get the time position
			MopidyService.getTimePosition().then( function(position){
				state.playPosition = position;
			});
		
		// we've been parsed the time position, so just use that
		}else{
			state.playPosition = newPosition;
		}
	}
	
	
	/**
	 * Update volume
	 * Fetches (if required) the volume from mopidy and sets to state
	 * @param volume = int (optional)
	 **/
	function updateVolume( newVolume ){
	
		// if we've been told what the new volume is, let's just use that
		if( typeof( newVolume ) !== 'undefined' ){
			state.volume = newVolume;
			
		// not told what new vol is, so let's fetch and set
		}else{
			MopidyService.getVolume().then(function( volume ){
				state.volume = volume;
			});
		}
	}
	
	
	/**
	 * Update the state of the player
	 * @param newState = string (optional)
	 **/
	function updatePlayerState( newState ){
		
		// if we've been told what the new state is, let's just use that
		if( typeof( newState ) !== 'undefined' ){
			if( newState == 'playing' )
				state.playing = true;
			else
				state.playing = false;
			
			updateWindowTitle();
				
		// not sure of new state, so let's find out first
		}else{
			MopidyService.getState().then( function( newState ){
				if( newState == 'playing' )
					state.playing = true;
				else
					state.playing = false;
				
				updateWindowTitle();
			});
		}
		
		// commented out due to strange behavior in Mopidy 1.1.1 where on pause, the play position was erratic
		// so let's just rely on our latest play position as factual. When we resume it'll re-fetch anyway.
		// updatePlayPosition();		
	};
	
	
	/**
	 * Update the current track
	 * This updates all instances of the track with new artwork, seek bar, window title, etc.
	 * @param tlTrack = the new track object (optional)
	 **/
	function updateCurrentTrack( tlTrack ){
		
		// update all ui uses of the track (window title, player bar, etc)
		var setCurrentTrack = function( tlTrack ){
		
			// save the current tltrack for global usage
			state.currentTlTrack = tlTrack;
			
			// now we have track info, let's get the spotify artwork	
			SpotifyService.getTrack( tlTrack.track.uri )
				.then(function( response ){
					state.currentTlTrack.track.album.images = response.album.images;
				});
			
			// update ui
			updatePlayPosition();
			updateWindowTitle();
		}
		
		// track provided, update pronto garcong!
		if( typeof( tlTrack ) !== 'undefined' ){
			setCurrentTrack( tlTrack );
			
		// no track provided, so go fetch it first, then proceed
		}else{
			
			MopidyService.getCurrentTlTrack().then( function( tlTrack ){
				if(tlTrack !== null && tlTrack !== undefined){
					if(tlTrack.track.name.indexOf("[loading]") > -1){
						MopidyService.lookup(tlTrack.track.uri).then(function(result){
							setCurrentTrack(result[0]);
						});
					}else{
						setCurrentTrack(tlTrack);
					}
				}
			});
		}
	};	
		

	/**
	 * Update browser title
	 **/
	function updateWindowTitle(){
	
		var track = state.currentTlTrack.track;
        var newTitle = 'No track playing';
		
        if( track ){
            var documentIcon = '\u25A0 ';
            var artistString = '';
            
            $.each(track.artists, function(key,value){
                if( artistString != '' )
                    artistString += ', ';
                artistString += value.name;
            });

            if( state.playing )
                documentIcon = '\u25B6 ';

            newTitle = documentIcon +' '+ track.name +' - '+ artistString;        
        };
        
		document.title = newTitle;
	}
	
	
	
	/**
	 * Update play progress position slider
	 **/
	$interval( 
		function(){
			if( state.playing ){
				state.playPosition += 1000;
			}
		},
		1000
	);
	
    
	/**
	 * Shortcut keys
	 **/
	$rootScope.$on('spotmop:keyboardShortcut:space', function( event ){
		if( state.playing ) var icon = 'pause'; else var icon = 'play';
		service.playPause();
		NotifyService.shortcut( icon );
    });
	$rootScope.$on('spotmop:keyboardShortcut:right', function( event ){		
		if( $rootScope.ctrlKeyHeld ){
			service.next();
			NotifyService.shortcut( 'forward' );
		}
    });
	$rootScope.$on('spotmop:keyboardShortcut:left', function( event ){    
		if( $rootScope.ctrlKeyHeld ){
			service.previous();
			NotifyService.shortcut( 'backward' );
		}
    });
	$rootScope.$on('spotmop:keyboardShortcut:up', function( event ){
		if( $rootScope.ctrlKeyHeld ){
			state.volume += 10;
			
			// don't let the volume exceed maximum possible, 100%
			if( state.volume >= 100 )
				state.volume = 100;
			service.setVolume( state.volume );
			NotifyService.shortcut( 'volume-up' );
		}
    });
	$rootScope.$on('spotmop:keyboardShortcut:down', function( event ){
		if( $rootScope.ctrlKeyHeld ){
			state.volume -= 10;
			
			// don't let the volume below minimum possible, 0%
			if( state.volume < 0 )
				state.volume = 0;
			service.setVolume( state.volume );
			NotifyService.shortcut( 'volume-down' );
		}
    });	
	
	
	/**
	 * Setup response object
	 * This is the object that is available to all controllers
	 **/
	var service = {
		
		state: function(){
			return state;
		},
		
		playPause: function(){
			if( state.playing ){
				MopidyService.pause();
				state.playing = false;
			}else{
				MopidyService.play();
				state.playing = true;
			}
		},
		
		stop: function(){
			MopidyService.stopPlayback();
			state.playing = false;
		},
		
		next: function(){
		
			// log this skip (we do this BEFORE moving to the next, as the skip is on the OLD track)
			if( SettingsService.getSetting('echonestenabled',false) )
				EchonestService.addToTasteProfile( 'skip', state.currentTlTrack.track.uri );
		
			MopidyService.play();
			MopidyService.next();
		},
		
		previous: function(){
			MopidyService.previous();
		},
		
		seek: function( time ){
			state.playPosition = time;
			MopidyService.seek( time );
		},
		
		setVolume: function( percent ){
			state.volume = percent;
			MopidyService.setVolume( percent );
		},
		
		/**
		 * Playback behavior toggles
		 **/		
		toggleRepeat: function(){
			if( state.isRepeat )
				MopidyService.setRepeat( false ).then( function(response){ state.isRepeat = false; } );
			else
				MopidyService.setRepeat( true ).then( function(response){ state.isRepeat = true; } );
			console.log( state );
		},		
		toggleRandom: function(){
			if( state.isRandom )
				MopidyService.setRandom( false ).then( function(response){ state.isRandom = false; } );
			else
				MopidyService.setRandom( true ).then( function(response){ state.isRandom = true; } );
		},		
		toggleMute: function(){
			if( state.isMute )
				MopidyService.setMute( false ).then( function(response){ state.isMute = false; } );
			else
				MopidyService.setMute( true ).then( function(response){ state.isMute = true; } );
		}
		
	};
	 
	return service;
	
}]);





