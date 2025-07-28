export function capitalise(name) {
    let lower = name.trim().toLowerCase();

    return lower.charAt(0).toUpperCase() + lower.slice(1);

}