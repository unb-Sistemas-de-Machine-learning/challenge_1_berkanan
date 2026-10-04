import type { RouteObject } from 'react-router-dom'

interface RouteMeta<
  RouteObjectType extends RouteObject = RouteObject,
> {
  relativePath: string
  childrenIndex: number
  route: RouteObjectType
}

interface RouteBranch<
  RouteObjectType extends RouteObject = RouteObject,
> {
  path: string
  routesMeta: RouteMeta<RouteObjectType>[]
}

function flattenRoutes<
  RouteObjectType extends RouteObject = RouteObject,
>(
  routes: RouteObjectType[],
  branches: RouteBranch<RouteObjectType>[] = [],
  parentsMeta: RouteMeta<RouteObjectType>[] = [],
  parentPath = '',
  _hasParentOptionalSegments = false,
): RouteBranch<RouteObjectType>[] {
  const flattenRoute = (
    route: RouteObjectType,
    index: number,
    hasParentOptionalSegments = _hasParentOptionalSegments,
    relativePath?: string,
  ) => {
    const meta: RouteMeta<RouteObjectType> = {
      relativePath:
        relativePath === undefined ? route.path || '' : relativePath,
      childrenIndex: index,
      route,
    }

    if (meta.relativePath.startsWith('/')) {
      if (
        !meta.relativePath.startsWith(parentPath)
        && hasParentOptionalSegments
      ) {
        return
      }
      meta.relativePath = meta.relativePath.slice(parentPath.length)
    }

    const path = joinPaths([parentPath, meta.relativePath])
    const routesMeta = parentsMeta.concat(meta)

    if (route.children && route.children.length > 0) {
      flattenRoutes(
        route.children,
        branches,
        routesMeta,
        path,
        hasParentOptionalSegments,
      )
    }

    if (route.path == null && !route.index) {
      return
    }

    branches.push({
      path,
      routesMeta,
    })
  }
  routes.forEach((route, index) => {
    if (route.path === '' || !route.path?.includes('?')) {
      flattenRoute(route, index)
    }
    else {
      for (const exploded of explodeOptionalSegments(route.path)) {
        flattenRoute(route, index, true, exploded)
      }
    }
  })

  return branches
}

function explodeOptionalSegments(path: string): string[] {
  const segments = path.split('/')
  if (segments.length === 0)
    return []

  const [first, ...rest] = segments

  const isOptional = first.endsWith('?')
  const required = first.replace(/\?$/, '')

  if (rest.length === 0) {
    return isOptional ? [required, ''] : [required]
  }

  const restExploded = explodeOptionalSegments(rest.join('/'))

  const result: string[] = []

  result.push(
    ...restExploded.map(subpath =>
      subpath === '' ? required : [required, subpath].join('/'),
    ),
  )

  if (isOptional) {
    result.push(...restExploded)
  }

  return result.map(exploded =>
    path.startsWith('/') && exploded === '' ? '/' : exploded,
  )
}

function joinPaths(paths: string[]): string {
  return paths.join('/').replace(/\/{2,}/g, '/')
}

export {
  flattenRoutes,
}
