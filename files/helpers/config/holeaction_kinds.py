HOLEACTION_KINDS = {
	'exile_user': {
		"str": 'exiled user {self.target_link}',
		"icon": 'fa-user-slash',
		"color": 'bg-danger'
	},
	'unexile_user': {
		"str": 'unexiled user {self.target_link}',
		"icon": 'fa-user',
		"color": 'bg-success'
	},
	'make_mod': {
		"str": 'made {self.target_link} a mod',
		"icon": 'fa-user-crown',
		"color": 'bg-success'
	},
	'remove_mod': {
		"str": 'removed {self.target_link} as mod',
		"icon": 'fa-user-crown',
		"color": 'bg-danger'
	},
	'change_hole': {
		"str": 'changed hole of {self.target_link}',
		"icon": 'fa-manhole',
		"color": 'bg-primary'
	},
	'flair_post': {
		"str": 'set a flair on {self.target_link}',
		"icon": 'fa-tag',
		"color": 'bg-primary'
	},
	'edit_sidebar': {
		"str": 'edited the sidebar',
		"icon": 'fa-columns',
		"color": 'bg-primary'
	},
	'edit_snappy_quotes': {
		"str": 'edited snappy quotes',
		"icon": 'fa-robot',
		"color": 'bg-primary'
	},
	'edit_css': {
		"str": 'edited the css',
		"icon": 'fa-palette',
		"color": 'bg-primary'
	},
	'upload_banner': {
		"str": 'uploaded a banner',
		"icon": 'fa-landscape',
		"color": 'bg-primary'
	},
	'delete_banner': {
		"str": 'deleted a banner',
		"icon": 'fa-image-slash',
		"color": 'bg-danger',
	},
	'upload_sidebar_image': {
		"str": 'uploaded a sidebar image',
		"icon": 'fa-image',
		"color": 'bg-primary'
	},
	'delete_sidebar_image': {
		"str": 'deleted a sidebar image',
		"icon": 'fa-image-slash',
		"color": 'bg-danger',
	},
	'change_marsey': {
		"str": 'changed the hole marsey',
		"icon": 'fa-cat',
		"color": 'bg-primary'
	},
	'pin_post': {
		"str": 'pinned post {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-success'
	},
	'unpin_post': {
		"str": 'unpinned post {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-muted'
	},
	'pin_comment': {
		"str": 'pinned {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-success'
	},
	'unpin_comment': {
		"str": 'unpinned {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-muted'
	},
	'enable_public_use': {
		"str": 'enabled public use mode',
		"icon": 'fa-users',
		"color": 'bg-primary'
	},
	'disable_public_use': {
		"str": 'disabled public use mode',
		"icon": 'fa-users',
		"color": 'bg-muted'
	},
	'enable_stealth': {
		"str": 'enabled stealth mode',
		"icon": 'fa-user-ninja',
		"color": 'bg-primary'
	},
	'disable_stealth': {
		"str": 'disabled stealth mode',
		"icon": 'fa-user-ninja',
		"color": 'bg-muted'
	},
	'set_nsfw': {
		"str": 'set nsfw on post {self.target_link}',
		"icon": 'fa-eye-evil',
		"color": 'bg-danger'
	},
	'unset_nsfw': {
		"str": 'un-set nsfw on post {self.target_link}',
		"icon": 'fa-eye-evil',
		"color": 'bg-success'
	},
	'set_nsfw_comment': {
		"str": 'set nsfw on a {self.target_link}',
		"icon": 'fa-eye-evil',
		"color": 'bg-danger'
	},
	'unset_nsfw_comment': {
		"str": 'un-set nsfw on a {self.target_link}',
		"icon": 'fa-eye-evil',
		"color": 'bg-success'
	},
	'distinguish_comment': {
		"str": 'distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-success'
	},
	'undistinguish_comment': {
		"str": 'un-distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-muted'
	},
	'distinguish_post': {
		"str": 'distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-success'
	},
	'undistinguish_post': {
		"str": 'un-distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-muted'
	},
	'resurrect_hole': {
		"str": 'resurrected the hole',
		"icon": 'fa-hand',
		"color": 'bg-primary'
	},
}

HOLEACTION_KINDS = dict(sorted(HOLEACTION_KINDS.items()))
