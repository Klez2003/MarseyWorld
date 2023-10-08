// This code isn't for feeble minds, you might not understand it Dr. Transmisia.
// The dainty hands of a trans goddess wrote this code. Watch the way her fingers
// dance across the keyboard and learn.

/**
 * @typedef {object} EmojiDef
 * @property {number} author_id
 * @property {string} author_original_username
 * @property {string} author_username
 * @property {number} count
 * @property {number} created_utc
 * @property {string} kind
 * @property {string} name
 * @property {number | null} submitter_id
 * @property {string[]} tags
 */

/** Returns a promise which can be used to await when the event loop is idle. */
const idle = () => {
    return new Promise(resolve => {
        requestIdleCallback(resolve);
    });
}

class TagDict {
    /** 
     * @type {Map<string,Set<string>>}
     * @private
     */
    _map = new Map();

    /**
     * @param {string} tag
     */
    get = (tag) => {
        const set = this._map.get(tag);

        if (!set) {
            const newSet = new Set();
            this._map.set(tag, newSet);
            return newSet;
        } else {
            return set;
        }
    }

    /**
     * @param {string} tag
     * @param {string} emojiName
     */
    add = (tag, emojiName) => {
        this.get(tag).add(emojiName);
    }

    /**
     * @param {string} tag
     * @param {string} emojiName
     */
    delete = (tag, emojiName) => {
        this.get(tag).delete(emojiName);
    }

    /**
     * If emojiName is not provided, returns whether the tag exists.
     * Otherwise, returns whether the tag contains the emoji.
     * @param {string} tag
     * @param {string} [emojiName]
     */
    has = (tag, emojiName) => {
        if (emojiName) {
            return this.get(tag).has(emojiName);
        } else {
            return this._map.has(tag);
        }
    }

    [Symbol.iterator] = () => this._map[Symbol.iterator]();
}

class EmojiEngine {
    tags = new TagDict();

    /**
     * @param {EmojiDef[]} emojis
     */
    init = async (emojis) => {
        for (const emoji of emojis) {
            this.tags.add(emoji.name, emoji.name);

            for (const tag of emoji.tags) {
                this.tags.add(tag, emoji.name);
            }

            // I left out tagging by author... lets see if anyone complains...
        }
    }

    search = async(query) => {
        if (query?.length < 2) {
            return new Set();
        }

        const results = new Set();
        for (const [tag, names] of this.tags) {
            if (tag.includes(query) || query.includes(tag)) {
                for (const name of names) {
                    results.add(name);
                }
            }
        }
        return results;
    }
}

const emojiEngine = new EmojiEngine();
emojiEngine.init();